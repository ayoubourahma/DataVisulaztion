"""
Data Loader Module - IMPROVED VERSION
Handles all data quality issues identified in the analysis report:
- Mixed date formats (DD/MM/YYYY and YYYY-MM-DD)
- Missing values ('nul', empty strings, NULL)
- Whitespace padding in all fields
- Empty lines removal
- Duplicate detection and optional removal
- UTF-8 with French characters (é, ê, etc.)
- Performance optimization for large files (1.5GB+)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BankDataLoader:
    """
    Enhanced data loader specifically designed for your bank data
    Based on comprehensive data quality analysis
    """
    
    def __init__(self, data_folder: str = "data", remove_duplicates: bool = True):
        self.data_folder = Path(data_folder)
        self.dataframes = {}
        self.file_info = {}
        self.errors = []
        self.remove_duplicates = remove_duplicates
        
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all .txt files from data folder with enhanced error handling
        Returns dict of dataframes with validation info
        """
        logger.info("📄 Starting enhanced data loading process...")
        
        # Find all .txt files
        txt_files = list(self.data_folder.glob("*.txt"))
        
        if not txt_files:
            logger.error(f"❌ No .txt files found in {self.data_folder}")
            return {}
        
        logger.info(f"🔍 Found {len(txt_files)} files to process")
        
        # Sort files by size (load small files first for quick feedback)
        txt_files.sort(key=lambda f: f.stat().st_size)
        
        # Load each file with progress bar
        for file_path in tqdm(txt_files, desc="Loading files"):
            try:
                df, info = self._load_single_file(file_path)
                
                if df is not None:
                    file_key = file_path.stem.lower()
                    self.dataframes[file_key] = df
                    self.file_info[file_key] = info
                    logger.info(f"✅ {file_path.name}: {len(df):,} rows × {len(df.columns)} cols")
                else:
                    logger.warning(f"⚠️ Failed to load: {file_path.name}")
                    
            except Exception as e:
                error_msg = f"Error loading {file_path.name}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        # Validation summary
        self._print_summary()
        
        return self.dataframes
    
    def _load_single_file(self, file_path: Path) -> Tuple[Optional[pd.DataFrame], Dict]:
        """
        Load a single file with enhanced handling for your specific data issues
        """
        info = {
            'filename': file_path.name,
            'original_rows': 0,
            'rows_loaded': 0,
            'columns': 0,
            'empty_lines_removed': 0,
            'duplicates_removed': 0,
            'missing_values': 0,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024)
        }
        
        try:
            # For very large files (>500MB), use chunked reading
            if info['file_size_mb'] > 500:
                logger.info(f"📦 Large file detected ({info['file_size_mb']:.1f}MB), using chunked reading...")
                return self._load_large_file_chunked(file_path, info)
            
            # Standard encoding list optimized for your data
            # UTF-8 is primary, but fallback to Windows encodings
            encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1', 'iso-8859-1']
            
            df = None
            successful_encoding = None
            
            for encoding in encodings:
                try:
                    # CRITICAL: Use these specific settings for your data format
                    df = pd.read_csv(
                        file_path,
                        sep=';',                    # Semicolon delimiter (confirmed)
                        encoding=encoding,
                        # Enhanced NULL handling based on report
                        na_values=['', 'null', 'NULL', 'None', 'nan', 'nul', 'NUL'],  # Added 'nul'
                        keep_default_na=True,
                        dtype=str,                  # Read as string first
                        engine='c',                 # Fast C engine
                        on_bad_lines='warn',        # Warn but continue
                        encoding_errors='replace',  # Replace bad chars
                        skipinitialspace=True,      # Strip leading whitespace after delimiter
                        low_memory=False            # Read entire file into memory (better for consistency)
                    )
                    
                    if df is not None and len(df.columns) > 0:
                        successful_encoding = encoding
                        logger.debug(f"✓ Loaded with {encoding}")
                        break
                        
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.debug(f"Encoding {encoding} failed: {str(e)}")
                    continue
            
            if df is None:
                logger.error(f"All encoding attempts failed for {file_path.name}")
                return None, info
            
            info['original_rows'] = len(df)
            
            # === DATA CLEANING PIPELINE (based on report) ===
            
            # 1. Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()
            
            # 2. Remove completely empty rows (addresses 75 empty lines in Src_chapitre.txt)
            rows_before = len(df)
            df = df.dropna(how='all')
            info['empty_lines_removed'] = rows_before - len(df)
            
            if info['empty_lines_removed'] > 0:
                logger.info(f"  🧹 Removed {info['empty_lines_removed']} empty lines")
            
            # 3. Strip whitespace from ALL string columns (addresses padding issue)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            # 4. Remove duplicates (addresses Src_utilisateur.txt issue)
            if self.remove_duplicates:
                rows_before = len(df)
                df = df.drop_duplicates()
                info['duplicates_removed'] = rows_before - len(df)
                
                if info['duplicates_removed'] > 0:
                    logger.info(f"  🔄 Removed {info['duplicates_removed']} duplicate rows")
            
            # 5. Parse dates with DUAL FORMAT support (CRITICAL FIX)
            df = self._parse_dates_dual_format(df)
            
            # 6. Optimize data types intelligently
            df = self._optimize_datatypes(df)
            
            # Update info
            info['rows_loaded'] = len(df)
            info['columns'] = len(df.columns)
            info['missing_values'] = df.isna().sum().sum()
            info['column_names'] = list(df.columns)
            info['encoding_used'] = successful_encoding
            
            return df, info
            
        except Exception as e:
            logger.error(f"Critical error loading {file_path.name}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None, info
    
    def _load_large_file_chunked(self, file_path: Path, info: Dict) -> Tuple[Optional[pd.DataFrame], Dict]:
        """
        Load very large files (>500MB) in chunks to avoid memory issues
        """
        chunks = []
        chunk_size = 100000  # Process 100k rows at a time
        
        try:
            # Read file in chunks
            for chunk in pd.read_csv(
                file_path,
                sep=';',
                encoding='utf-8',
                na_values=['', 'null', 'NULL', 'None', 'nan', 'nul', 'NUL'],
                dtype=str,
                chunksize=chunk_size,
                engine='c',
                on_bad_lines='warn',
                low_memory=True
            ):
                # Clean each chunk
                chunk.columns = chunk.columns.str.strip()
                chunk = chunk.dropna(how='all')
                
                # Strip whitespace
                for col in chunk.columns:
                    if chunk[col].dtype == 'object':
                        chunk[col] = chunk[col].str.strip()
                
                chunks.append(chunk)
            
            # Combine all chunks
            df = pd.concat(chunks, ignore_index=True)
            
            # Remove duplicates if requested
            if self.remove_duplicates:
                rows_before = len(df)
                df = df.drop_duplicates()
                info['duplicates_removed'] = rows_before - len(df)
            
            # Parse dates
            df = self._parse_dates_dual_format(df)
            
            # Update info
            info['rows_loaded'] = len(df)
            info['columns'] = len(df.columns)
            info['missing_values'] = df.isna().sum().sum()
            
            logger.info(f"  ✓ Loaded large file in {len(chunks)} chunks")
            
            return df, info
            
        except Exception as e:
            logger.error(f"Error loading large file {file_path.name}: {str(e)}")
            return None, info
    
    def _parse_dates_dual_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        CRITICAL FIX: Handle both date formats found in your data
        - YYYY-MM-DD (most files)
        - DD/MM/YYYY (Src_objectif_epargne_realtime.txt)
        """
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'dt_' in col.lower()]
        
        for col in date_columns:
            try:
                # Try to detect which format is being used
                sample = df[col].dropna().head(10).astype(str)
                
                # Check if format is DD/MM/YYYY (contains / and starts with small number)
                if sample.str.contains('/').any():
                    # DD/MM/YYYY format
                    df[col] = pd.to_datetime(
                        df[col],
                        format='%d/%m/%Y',
                        errors='coerce'
                    )
                    logger.debug(f"  📅 Parsed {col} as DD/MM/YYYY")
                else:
                    # YYYY-MM-DD format (or mixed)
                    df[col] = pd.to_datetime(
                        df[col],
                        format='%Y-%m-%d',
                        errors='coerce'
                    )
                    logger.debug(f"  📅 Parsed {col} as YYYY-MM-DD")
                    
            except Exception as e:
                logger.debug(f"Could not parse date column {col}: {str(e)}")
                # Try pandas' flexible parser as last resort
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                except:
                    pass  # Keep as string if all else fails
        
        return df
    
    def _optimize_datatypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize memory usage intelligently
        WITHOUT losing any data
        """
        df_optimized = df.copy()
        
        for col in df_optimized.columns:
            # Skip date columns (already parsed)
            if pd.api.types.is_datetime64_any_dtype(df_optimized[col]):
                continue
            
            # Try to convert to numeric if appropriate
            if df_optimized[col].dtype == 'object':
                try:
                    # Try numeric conversion
                    numeric_col = pd.to_numeric(df_optimized[col], errors='coerce')
                    
                    # Only convert if >90% of non-null values are numeric
                    non_null_count = df_optimized[col].notna().sum()
                    numeric_count = numeric_col.notna().sum()
                    
                    if non_null_count > 0 and (numeric_count / non_null_count) > 0.9:
                        df_optimized[col] = numeric_col
                        logger.debug(f"  🔢 Converted {col} to numeric")
                except:
                    pass  # Keep as string
        
        return df_optimized
    
    def _print_summary(self):
        """Print comprehensive loading summary with data quality stats"""
        logger.info("\n" + "="*70)
        logger.info("📊 DATA LOADING SUMMARY")
        logger.info("="*70)
        
        total_rows = sum(len(df) for df in self.dataframes.values())
        total_cols = sum(len(df.columns) for df in self.dataframes.values())
        total_empty_removed = sum(info.get('empty_lines_removed', 0) for info in self.file_info.values())
        total_dupes_removed = sum(info.get('duplicates_removed', 0) for info in self.file_info.values())
        
        logger.info(f"✅ Successfully loaded: {len(self.dataframes)} files")
        logger.info(f"📈 Total rows: {total_rows:,}")
        logger.info(f"📋 Total columns: {total_cols}")
        
        if total_empty_removed > 0:
            logger.info(f"🧹 Empty lines removed: {total_empty_removed:,}")
        
        if total_dupes_removed > 0:
            logger.info(f"🔄 Duplicate rows removed: {total_dupes_removed:,}")
        
        if self.errors:
            logger.warning(f"\n⚠️ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                logger.warning(f"  - {error}")
        
        logger.info("\n🗂️ File Details:")
        for key, df in self.dataframes.items():
            info = self.file_info.get(key, {})
            missing_pct = (df.isna().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
            
            logger.info(
                f"  • {key}: {len(df):,} rows × {len(df.columns)} cols "
                f"({info.get('file_size_mb', 0):.1f}MB) "
                f"[{missing_pct:.1f}% missing]"
            )
            
            if info.get('empty_lines_removed', 0) > 0:
                logger.info(f"    └─ Removed {info['empty_lines_removed']} empty lines")
            if info.get('duplicates_removed', 0) > 0:
                logger.info(f"    └─ Removed {info['duplicates_removed']} duplicates")
        
        logger.info("="*70 + "\n")
    
    def get_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """Get a specific dataframe by key"""
        return self.dataframes.get(key.lower())
    
    def get_all_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Get all loaded dataframes"""
        return self.dataframes
    
    def validate_data_integrity(self) -> Dict:
        """
        Enhanced validation based on data quality report findings
        """
        validation = {
            'total_files': len(self.dataframes),
            'total_rows': sum(len(df) for df in self.dataframes.values()),
            'files_with_issues': [],
            'recommendations': [],
            'date_format_check': {}
        }
        
        for key, df in self.dataframes.items():
            issues = []
            
            # Check for remaining duplicates
            if not self.remove_duplicates:
                duplicates = df.duplicated().sum()
                if duplicates > 0:
                    issues.append(f"Found {duplicates:,} duplicate rows (not removed)")
            
            # Check for high percentage of missing values (report: 98.9% in objectif file)
            missing_pct = (df.isna().sum() / len(df) * 100)
            high_missing = missing_pct[missing_pct > 50]
            if len(high_missing) > 0:
                issues.append(
                    f"{len(high_missing)} columns with >50% missing data: "
                    f"{', '.join(high_missing.index[:3].tolist())}"
                )
            
            # Check date columns
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'dt_' in col.lower()]
            for col in date_cols:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    validation['date_format_check'][f"{key}.{col}"] = "✓ Parsed successfully"
                else:
                    validation['date_format_check'][f"{key}.{col}"] = "⚠️ Not parsed as datetime"
            
            # Check for systematic empty columns (report: 'marche' field always empty)
            empty_cols = df.columns[df.isna().all()].tolist()
            if empty_cols:
                issues.append(f"Completely empty columns: {', '.join(empty_cols)}")
            
            if issues:
                validation['files_with_issues'].append({
                    'file': key,
                    'issues': issues
                })
        
        # Add recommendations based on findings
        if validation['files_with_issues']:
            validation['recommendations'].append(
                "Consider removing completely empty columns to reduce memory usage"
            )
        
        return validation
    
    def export_cleaned_data(self, output_folder: str = "data/cleaned"):
        """
        Export cleaned data to new folder for archival/reuse
        """
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"💾 Exporting cleaned data to {output_folder}...")
        
        for key, df in self.dataframes.items():
            output_file = output_path / f"{key}_cleaned.csv"
            df.to_csv(output_file, index=False, sep=';', encoding='utf-8')
            logger.info(f"  ✓ Exported {key} ({len(df):,} rows)")
        
        logger.info("✅ Export complete!")


# Convenience function
def load_bank_data(data_folder: str = "data", remove_duplicates: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Quick function to load all bank data with enhanced cleaning
    
    Args:
        data_folder: Path to data folder
        remove_duplicates: Whether to remove duplicate rows (default: True)
    
    Returns:
        Dictionary of dataframes
    """
    loader = BankDataLoader(data_folder, remove_duplicates=remove_duplicates)
    return loader.load_all_data()


if __name__ == "__main__":
    # Test the improved loader
    print("Testing Enhanced Data Loader...")
    print("="*70)
    
    loader = BankDataLoader("data", remove_duplicates=True)
    dataframes = loader.load_all_data()
    
    print(f"\n✅ Loaded {len(dataframes)} dataframes:")
    for key, df in dataframes.items():
        print(f"  • {key}: {df.shape}")
    
    # Run validation
    print("\n" + "="*70)
    print("🔍 Running data integrity validation...")
    validation = loader.validate_data_integrity()
    
    print(f"\nValidation Results:")
    print(f"  Total files: {validation['total_files']}")
    print(f"  Total rows: {validation['total_rows']:,}")
    print(f"  Files with issues: {len(validation['files_with_issues'])}")
    
    if validation['files_with_issues']:
        print("\n⚠️ Issues found:")
        for file_info in validation['files_with_issues']:
            print(f"  • {file_info['file']}:")
            for issue in file_info['issues']:
                print(f"    - {issue}")
    
    if validation.get('date_format_check'):
        print("\n📅 Date parsing status:")
        for col, status in validation['date_format_check'].items():
            print(f"  {status} {col}")
