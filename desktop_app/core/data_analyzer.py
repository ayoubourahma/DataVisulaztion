"""
Background Data Analyzer
Pre-processes data for AI to use
"""

import pandas as pd
import numpy as np
from typing import Dict
import json
from pathlib import Path
import pickle


class DataAnalyzer:
    """Analyzes data in background and creates AI-ready summaries"""
    
    def __init__(self, dataframes: Dict[str, pd.DataFrame]):
        self.dataframes = dataframes
        self.analysis_cache = {}
        
    def analyze_all(self) -> Dict:
        """Run full analysis on all dataframes"""
        results = {
            'summary': self.create_summary(),
            'statistics': self.compute_statistics(),
            'insights': self.extract_insights(),
            'searchable_data': self.create_searchable_index()
        }
        return results
    
    def create_summary(self) -> Dict:
        """Create high-level summary"""
        summary = {
            'total_files': len(self.dataframes),
            'total_rows': sum(len(df) for df in self.dataframes.values()),
            'total_columns': sum(len(df.columns) for df in self.dataframes.values()),
            'file_details': {}
        }
        
        for name, df in self.dataframes.items():
            summary['file_details'][name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
                'null_count': df.isnull().sum().sum(),
                'column_types': df.dtypes.value_counts().to_dict()
            }
        
        return summary
    
    def compute_statistics(self) -> Dict:
        """Compute key statistics for AI"""
        stats = {}
        
        # Customer stats
        if 'src_utilisateur' in self.dataframes:
            df = self.dataframes['src_utilisateur']
            stats['customers'] = {
                'total': len(df),
                'segments': df['segment'].value_counts().to_dict() if 'segment' in df.columns else {},
                'nationalities': df['nationalite_client'].value_counts().to_dict() if 'nationalite_client' in df.columns else {},
                'agencies': df['ch_code_agence'].nunique() if 'ch_code_agence' in df.columns else 0,
                'sectors': df['secteur_activite'].value_counts().head(10).to_dict() if 'secteur_activite' in df.columns else {}
            }
        
        # Activity stats
        if 'src_activité_applicative_adria' in self.dataframes:
            df = self.dataframes['src_activité_applicative_adria']
            stats['activity'] = {
                'total_sessions': pd.to_numeric(df['nombre_sessions'], errors='coerce').sum() if 'nombre_sessions' in df.columns else 0,
                'unique_users': df['ch_code_client'].nunique() if 'ch_code_client' in df.columns else 0,
                'date_range': {
                    'min': str(pd.to_datetime(df['date_jour'], errors='coerce').min()) if 'date_jour' in df.columns else None,
                    'max': str(pd.to_datetime(df['date_jour'], errors='coerce').max()) if 'date_jour' in df.columns else None
                }
            }
        
        # Savings stats
        if 'src_objectif_epargne_cmc' in self.dataframes:
            df = self.dataframes['src_objectif_epargne_cmc']
            month_cols = [f'M_{i}' for i in range(1, 13)]
            monthly_avgs = {}
            for col in month_cols:
                if col in df.columns:
                    avg = pd.to_numeric(df[col], errors='coerce').mean()
                    monthly_avgs[col] = float(avg) if not pd.isna(avg) else 0
            
            stats['savings'] = {
                'total_accounts': len(df),
                'monthly_averages': monthly_avgs,
                'total_cmc': float(pd.to_numeric(df['CMC'], errors='coerce').sum()) if 'CMC' in df.columns else 0,
                'segments': df['Segment_NMR'].value_counts().to_dict() if 'Segment_NMR' in df.columns else {}
            }
        
        return stats
    
    def extract_insights(self) -> Dict:
        """Extract key insights for AI - Focus on Tunisian savings opportunities"""
        insights = {
            'top_findings': [],
            'recommendations': [],
            'spending_patterns': []
        }
        
        # Top customers by segment
        if 'src_utilisateur' in self.dataframes:
            df = self.dataframes['src_utilisateur']
            if 'segment' in df.columns:
                top_segment = df['segment'].value_counts().head(1)
                if len(top_segment) > 0:
                    insights['top_findings'].append(
                        f"Plus grand segment client: {top_segment.index[0]} avec {top_segment.values[0]:,} clients"
                    )
        
        # Activity patterns - identify frequent small transactions
        if 'src_activité_applicative_adria' in self.dataframes:
            df = self.dataframes['src_activité_applicative_adria']
            total_sessions = pd.to_numeric(df['nombre_sessions'], errors='coerce').sum()
            unique_users = df['ch_code_client'].nunique()
            if unique_users > 0:
                avg_sessions = total_sessions / unique_users
                insights['top_findings'].append(
                    f"Sessions moyennes par utilisateur: {avg_sessions:.1f}"
                )
                
                # High frequency users (potential for savings advice)
                if avg_sessions > 20:
                    insights['recommendations'].append(
                        "Utilisateurs à haute fréquence détectés - opportunité pour conseils d'épargne personnalisés"
                    )
        
        # Transaction type analysis
        if 'src_type_operation' in self.dataframes:
            df = self.dataframes['src_type_operation']
            insights['spending_patterns'].append(
                f"Types d'opérations disponibles: {len(df)} catégories pour analyse des dépenses"
            )
        
        # Savings patterns
        if 'src_objectif_epargne_cmc' in self.dataframes:
            df = self.dataframes['src_objectif_epargne_cmc']
            
            # Calculate average savings
            month_cols = [f'M_{i}' for i in range(1, 13)]
            monthly_values = []
            for col in month_cols:
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(vals) > 0:
                        monthly_values.extend(vals)
            
            if monthly_values:
                avg_monthly = np.mean(monthly_values)
                median_monthly = np.median(monthly_values)
                
                insights['top_findings'].append(
                    f"Épargne moyenne mensuelle: {avg_monthly:,.2f} TND"
                )
                insights['top_findings'].append(
                    f"Épargne médiane mensuelle: {median_monthly:,.2f} TND"
                )
                
                # Savings recommendations
                if avg_monthly < 100:
                    insights['recommendations'].append(
                        "Épargne moyenne faible - opportunité d'amélioration avec conseils ciblés"
                    )
                
                # Calculate potential savings from small daily expenses
                # Assumption: average Tunisian spends 5-10 TND/day on unnecessary items
                potential_daily_savings = 7.5  # TND
                potential_monthly = potential_daily_savings * 30
                potential_yearly = potential_monthly * 12
                
                insights['recommendations'].append(
                    f"Potentiel d'économie: Réduire dépenses quotidiennes de {potential_daily_savings} TND/jour "
                    f"= {potential_monthly} TND/mois = {potential_yearly} TND/an"
                )
        
        # Add Tunisian-specific savings tips
        insights['recommendations'].extend([
            "Café quotidien (3 TND) = 90 TND/mois = 1,080 TND/an - faire café à la maison économise 70 TND/mois",
            "Taxi quotidien (10 TND) vs Louage (3 TND) = économie de 210 TND/mois",
            "Restaurant midi (15 TND) vs repas maison (5 TND) = économie de 300 TND/mois",
            "Cigarettes (10 TND/jour) = 300 TND/mois = 3,600 TND/an - arrêter = grandes économies"
        ])
        
        return insights
    
    def create_searchable_index(self) -> Dict:
        """Create searchable index of data"""
        index = {
            'columns': {},
            'unique_values': {},
            'value_counts': {}
        }
        
        for name, df in self.dataframes.items():
            index['columns'][name] = list(df.columns)
            
            # Index unique values for key columns (limit to avoid huge index)
            for col in df.columns[:5]:  # First 5 columns only
                unique_vals = df[col].unique()
                if len(unique_vals) < 100:  # Only if reasonable number
                    index['unique_values'][f"{name}.{col}"] = [str(v) for v in unique_vals[:50]]
        
        return index
    
    def save_analysis(self, folder: str):
        """Save analysis to disk"""
        cache_path = Path(folder) / '.ai_analysis_cache.pkl'
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(self.analysis_cache, f)
        except Exception as e:
            print(f"Failed to save analysis cache: {e}")
    
    def load_analysis(self, folder: str) -> bool:
        """Load pre-computed analysis"""
        cache_path = Path(folder) / '.ai_analysis_cache.pkl'
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    self.analysis_cache = pickle.load(f)
                return True
            except:
                return False
        return False


def analyze_data_background(dataframes: Dict[str, pd.DataFrame], folder: str) -> Dict:
    """Run analysis in background and save results"""
    analyzer = DataAnalyzer(dataframes)
    
    # Check if we have cached analysis
    if analyzer.load_analysis(folder):
        return analyzer.analysis_cache
    
    # Run fresh analysis
    results = analyzer.analyze_all()
    analyzer.analysis_cache = results
    analyzer.save_analysis(folder)
    
    return results
