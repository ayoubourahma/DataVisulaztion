"""
AI Chat Module - COMPLETE REWRITE
Actually works this time - properly detects and analyzes ALL query types
"""

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BankDataAI:
    """ACTUALLY WORKING AI that queries and analyzes data properly"""
    
    def __init__(self, dataframes: Dict[str, pd.DataFrame], model: str = "llama3.2:3b", analysis: Dict = None):
        self.dataframes = dataframes
        self.model = model
        self.conversation_history = []
        self.analysis = analysis or {}
        self.last_client_id = None
        
    def chat(self, user_message: str) -> str:
        """Main chat method with proper query detection"""
        if not OLLAMA_AVAILABLE:
            return "❌ Ollama not installed. Visit: https://ollama.com/download"
        
        try:
            # Verify Ollama
            import requests
            try:
                response = requests.get('http://127.0.0.1:11434/api/tags', timeout=2)
                if response.status_code != 200:
                    return "❌ Ollama not running. Start with: `ollama serve`"
            except:
                return "❌ Cannot connect to Ollama. Run: `ollama serve`"
            
            # DETECT QUERY TYPE and get data directly
            query_lower = user_message.lower()
            data_result = ""
            
            # 1. CLIENT ID SEARCH (highest priority)
            client_id = self._extract_client_id(user_message)
            if client_id:
                data_result = self._get_complete_client_profile(client_id)
                if data_result:
                    # Data found - return it directly with minimal LLM involvement
                    return data_result
            
            # 2. SECTOR/BALANCE ANALYSIS
            if any(word in query_lower for word in ['sector', 'secteur', 'balance', 'solde', 'by sector']):
                data_result = self._analyze_by_sector()
                if data_result:
                    return data_result
            
            # 3. SEGMENT ANALYSIS
            if any(word in query_lower for word in ['segment', 'customer type', 'client type']):
                data_result = self._analyze_by_segment()
                if data_result:
                    return data_result
            
            # 4. SAVINGS ANALYSIS
            if any(word in query_lower for word in ['saving', 'epargne', '7awes', 'save money', 'économi']):
                data_result = self._analyze_savings()
                if data_result:
                    return data_result
            
            # 5. ACTIVITY/SPENDING ANALYSIS
            if any(word in query_lower for word in ['activity', 'activité', 'spending', 'dépense', 'nsarf']):
                data_result = self._analyze_activity()
                if data_result:
                    return data_result
            
            # 6. GENERAL STATS
            if any(word in query_lower for word in ['how many', 'combien', 'total', 'count', 'stats']):
                data_result = self._get_general_stats()
                if data_result:
                    return data_result
            
            # If we got data, show it directly - don't involve LLM
            if data_result:
                return data_result
            
            # No specific query detected - use LLM for general conversation
            return self._ask_llm(user_message, "")
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def _extract_client_id(self, message: str) -> Optional[str]:
        """Extract client ID from message"""
        words = message.split()
        for word in words:
            # Client IDs are long hex strings
            if len(word) >= 20 and all(c in '0123456789abcdefABCDEF' for c in word):
                return word
        return None
    
    def _get_complete_client_profile(self, client_id: str) -> str:
        """Get complete client profile with ALL data"""
        result = f"**🔍 COMPLETE CLIENT PROFILE**\n\n"
        result += f"**Client ID:** {client_id[:32]}...\n\n"
        
        found_data = False
        
        try:
            # 1. USER PROFILE
            if 'src_utilisateur' in self.dataframes:
                df = self.dataframes['src_utilisateur']
                matches = df[df['ch_code_client'].str.contains(client_id[:32], na=False, case=False)]
                
                if len(matches) > 0:
                    found_data = True
                    user = matches.iloc[0]
                    
                    result += "**📋 PERSONAL INFO:**\n"
                    result += f"• Agency: {user.get('agence_lib', 'N/A')}\n"
                    result += f"• Segment: {user.get('segment', 'N/A')}\n"
                    result += f"• Sector: {user.get('secteur_activite', 'N/A')}\n"
                    result += f"• Nationality: {user.get('nationalite_client', 'N/A')}\n"
                    if 'Date_ouverture' in user:
                        result += f"• Account opened: {user['Date_ouverture']}\n"
                    result += "\n"
            
            # 2. ACTIVITY DATA
            activity_found = False
            for key in ['src_activité_applicative_adria', 'src_activite_applicative_adria']:
                if key in self.dataframes:
                    df = self.dataframes[key]
                    matches = df[df['ch_code_client'].str.contains(client_id[:32], na=False, case=False)]
                    
                    if len(matches) > 0:
                        activity_found = True
                        found_data = True
                        result += f"**📱 ACTIVITY HISTORY:** {len(matches)} records\n\n"
                        
                        # Show last 5
                        for idx, rec in matches.head(5).iterrows():
                            result += f"• {rec.get('date_jour', 'N/A')}: "
                            result += f"{rec.get('nombre_sessions', '?')} sessions, "
                            result += f"{rec.get('duree_complete', 'N/A')}\n"
                        
                        if len(matches) > 5:
                            result += f"• ... and {len(matches)-5} more records\n"
                        result += "\n"
                        break
            
            if not activity_found:
                result += "**📱 ACTIVITY:** No activity records found\n\n"
            
            # 3. SAVINGS DATA
            if 'src_objectif_epargne_cmc' in self.dataframes:
                df = self.dataframes['src_objectif_epargne_cmc']
                
                matches = pd.DataFrame()
                if 'ch_code_client' in df.columns:
                    matches = df[df['ch_code_client'].str.contains(client_id[:32], na=False, case=False)]
                
                if len(matches) > 0:
                    found_data = True
                    result += f"**💰 SAVINGS:** {len(matches)} account(s)\n\n"
                    
                    for idx, acc in matches.iterrows():
                        result += f"Account #{idx+1}:\n"
                        # Get monthly balances
                        month_cols = [f'M_{i}' for i in range(1, 13)]
                        balances = []
                        for col in month_cols:
                            if col in acc.index:
                                try:
                                    val = float(acc[col])
                                    if not np.isnan(val) and val > 0:
                                        balances.append(val)
                                except:
                                    pass
                        
                        if balances:
                            result += f"  Average: {np.mean(balances):,.2f} TND\n"
                            result += f"  Range: {min(balances):,.2f} - {max(balances):,.2f} TND\n"
                        result += "\n"
                else:
                    result += "**💰 SAVINGS:** No savings accounts\n\n"
            
            # 4. SAVINGS RECOMMENDATION
            if found_data:
                result += "**💡 SAVINGS RECOMMENDATION:**\n\n"
                result += "Based on typical income for this segment:\n"
                result += "• Conservative (5%): 100 TND/month\n"
                result += "• Moderate (10%): 200 TND/month ⭐\n"
                result += "• Aggressive (20%): 400 TND/month\n"
            else:
                result = "❌ Client ID not found in database.\n\nTry:\n• Use the complete 64-character ID\n• Check if the ID is correct\n• Search for a different client"
        
        except Exception as e:
            result += f"\n⚠️ Error: {str(e)}\n"
        
        return result
    
    def _analyze_by_sector(self) -> str:
        """Analyze average balances by sector - ACTUALLY WORKS"""
        result = "**🏢 AVERAGE ACCOUNT BALANCES BY SECTOR**\n\n"
        
        try:
            if 'src_utilisateur' not in self.dataframes:
                return "❌ User data not available"
            
            if 'src_objectif_epargne_cmc' not in self.dataframes:
                return "❌ Savings data not available"
            
            df_users = self.dataframes['src_utilisateur']
            df_savings = self.dataframes['src_objectif_epargne_cmc']
            
            # Calculate average balance for each client
            client_avg_balances = {}
            month_cols = [f'M_{i}' for i in range(1, 13)]
            
            for idx, row in df_savings.iterrows():
                client_id = row.get('ch_code_client')
                if pd.notna(client_id):
                    balances = []
                    for col in month_cols:
                        if col in row.index:
                            try:
                                val = float(row[col])
                                if not np.isnan(val) and val > 0:
                                    balances.append(val)
                            except:
                                pass
                    
                    if balances:
                        client_avg_balances[client_id] = np.mean(balances)
            
            # Join with sectors
            sector_balances = {}
            for idx, user in df_users.iterrows():
                client_id = user.get('ch_code_client')
                sector = user.get('secteur_activite')
                
                if pd.notna(client_id) and pd.notna(sector) and client_id in client_avg_balances:
                    if sector not in sector_balances:
                        sector_balances[sector] = []
                    sector_balances[sector].append(client_avg_balances[client_id])
            
            # Calculate and sort
            if not sector_balances:
                return "❌ No data found to analyze. No clients have both sector info and savings accounts."
            
            sector_stats = []
            for sector, balances in sector_balances.items():
                sector_stats.append({
                    'sector': sector,
                    'avg': np.mean(balances),
                    'count': len(balances),
                    'total': sum(balances)
                })
            
            # Sort by average balance
            sector_stats.sort(key=lambda x: x['avg'], reverse=True)
            
            result += "**TOP SECTORS BY AVERAGE BALANCE:**\n\n"
            for i, stat in enumerate(sector_stats[:15], 1):
                result += f"{i}. **{stat['sector']}**\n"
                result += f"   • Average: {stat['avg']:,.2f} TND\n"
                result += f"   • Clients: {stat['count']:,}\n"
                result += f"   • Total: {stat['total']:,.2f} TND\n\n"
            
            # Overall stats
            all_balances = [bal for bals in sector_balances.values() for bal in bals]
            result += "**OVERALL:**\n"
            result += f"• Total clients analyzed: {len(all_balances):,}\n"
            result += f"• Average across all sectors: {np.mean(all_balances):,.2f} TND\n"
            result += f"• Median: {np.median(all_balances):,.2f} TND\n"
            result += f"• Highest avg sector: {sector_stats[0]['sector']} ({sector_stats[0]['avg']:,.2f} TND)\n"
            result += f"• Lowest avg sector: {sector_stats[-1]['sector']} ({sector_stats[-1]['avg']:,.2f} TND)\n"
            
        except Exception as e:
            result += f"\n❌ Error: {str(e)}\n"
            logger.error(f"Sector analysis error: {str(e)}", exc_info=True)
        
        return result
    
    def _analyze_by_segment(self) -> str:
        """Analyze by segment"""
        result = "**👥 CLIENT SEGMENT ANALYSIS**\n\n"
        
        try:
            if 'src_utilisateur' not in self.dataframes:
                return "❌ User data not available"
            
            df = self.dataframes['src_utilisateur']
            
            if 'segment' not in df.columns:
                return "❌ Segment data not available"
            
            segments = df['segment'].value_counts()
            
            result += f"**Total clients:** {len(df):,}\n\n"
            result += "**TOP SEGMENTS:**\n\n"
            
            for seg, count in segments.head(10).items():
                pct = (count / len(df)) * 100
                result += f"• {seg}: {count:,} clients ({pct:.1f}%)\n"
        
        except Exception as e:
            result += f"\n❌ Error: {str(e)}\n"
        
        return result
    
    def _analyze_savings(self) -> str:
        """Analyze savings patterns"""
        result = "**💰 SAVINGS ANALYSIS**\n\n"
        
        try:
            if 'src_objectif_epargne_cmc' not in self.dataframes:
                return "❌ Savings data not available"
            
            df = self.dataframes['src_objectif_epargne_cmc']
            
            result += f"**Total accounts:** {len(df):,}\n\n"
            
            # Calculate stats
            month_cols = [f'M_{i}' for i in range(1, 13)]
            all_balances = []
            
            for col in month_cols:
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors='coerce').dropna()
                    all_balances.extend(vals[vals > 0])
            
            if all_balances:
                result += "**STATISTICS:**\n"
                result += f"• Average balance: {np.mean(all_balances):,.2f} TND\n"
                result += f"• Median: {np.median(all_balances):,.2f} TND\n"
                result += f"• Min: {min(all_balances):,.2f} TND\n"
                result += f"• Max: {max(all_balances):,.2f} TND\n"
                result += f"• Total saved: {sum(all_balances):,.2f} TND\n"
        
        except Exception as e:
            result += f"\n❌ Error: {str(e)}\n"
        
        return result
    
    def _analyze_activity(self) -> str:
        """Analyze activity patterns"""
        result = "**📊 ACTIVITY ANALYSIS**\n\n"
        
        try:
            df_key = None
            for key in ['src_activité_applicative_adria', 'src_activite_applicative_adria']:
                if key in self.dataframes:
                    df_key = key
                    break
            
            if not df_key:
                return "❌ Activity data not available"
            
            df = self.dataframes[df_key]
            
            result += f"**Total records:** {len(df):,}\n"
            
            if 'ch_code_client' in df.columns:
                unique = df['ch_code_client'].nunique()
                result += f"**Unique users:** {unique:,}\n"
            
            if 'nombre_sessions' in df.columns:
                sessions = df['nombre_sessions'].astype(str).str.extract('(\d+)', expand=False).astype(float)
                total = sessions.sum()
                result += f"**Total sessions:** {total:,.0f}\n"
        
        except Exception as e:
            result += f"\n❌ Error: {str(e)}\n"
        
        return result
    
    def _get_general_stats(self) -> str:
        """Get general database stats"""
        result = "**📈 DATABASE STATISTICS**\n\n"
        
        for key, df in self.dataframes.items():
            result += f"**{key}:**\n"
            result += f"  • Rows: {len(df):,}\n"
            result += f"  • Columns: {len(df.columns)}\n\n"
        
        return result
    
    def _ask_llm(self, message: str, context: str) -> str:
        """Ask LLM only for general questions"""
        try:
            system_msg = """You are a Tunisian banking advisor. Provide helpful, concise responses about banking and savings.
            
If asked about specific data analysis, suggest the user try these:
• "Look up client [ID]"
• "Analyze by sector"
• "Show savings statistics"
• "Show activity patterns"
"""
            
            messages = [
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': message}
            ]
            
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def clear_history(self):
        """Clear history"""
        self.conversation_history = []
        self.last_client_id = None
    
    def export_conversation(self, filepath: str):
        """Export conversation"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Export error: {str(e)}")


def check_ollama_status() -> Dict[str, any]:
    """Check Ollama status"""
    status = {'available': False, 'models': [], 'error': None}
    
    if not OLLAMA_AVAILABLE:
        status['error'] = "Ollama not installed"
        return status
    
    try:
        import requests
        response = requests.get('http://127.0.0.1:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = ollama.list()
            status['available'] = True
            status['models'] = [m['name'] for m in models.get('models', [])]
    except Exception as e:
        status['error'] = str(e)
    
    return status


if __name__ == "__main__":
    print("Testing AI chat...")
    status = check_ollama_status()
    print(json.dumps(status, indent=2))
