"""
AI Insights Generator Service
Uses Azure OpenAI to generate actionable insights from EI Tech KPI data
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from config.azure_config import get_azure_openai_client, azure_config

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class AIInsightsGenerator:
    """Generates AI-powered insights from KPI data using Azure OpenAI"""
    
    def __init__(self):
        self.client = get_azure_openai_client()
        self.deployment_name = azure_config.azure_openai_deployment_name
        self.max_tokens = azure_config.max_tokens
        self.temperature = azure_config.temperature
    
    def generate_insights(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI insights from KPI data
        
        Args:
            kpi_data: Dictionary containing KPI metrics from EI Tech system
            
        Returns:
            Dictionary containing comprehensive insights in bullet point format
        """
        try:
            logger.info("Starting AI insights generation")
            
            # Prepare the data for analysis
            formatted_data = self._format_kpi_data_for_analysis(kpi_data)
            
            # Generate comprehensive insights
            insights_list = self._generate_comprehensive_insights(formatted_data)
            
            result = {
                "insights": insights_list,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "data_period": f"{kpi_data.get('query_metadata', {}).get('start_date', 'N/A')} to {kpi_data.get('query_metadata', {}).get('end_date', 'N/A')}",
                    "ai_model": self.deployment_name,
                    "total_insights": len(insights_list)
                }
            }
            
            logger.info("AI insights generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            raise
    
    def generate_additional_insights(self, kpi_data: Dict[str, Any], existing_insights: List[str], 
                                   positive_examples: List[str], count: int = 5, 
                                   focus_areas: List[str] = None) -> List[str]:
        """
        Generate additional AI insights that are different from existing ones
        
        Args:
            kpi_data: Dictionary containing KPI metrics
            existing_insights: List of already generated insights to avoid duplicates
            positive_examples: List of insights that received positive feedback
            count: Number of new insights to generate
            focus_areas: List of specific areas to focus on
            
        Returns:
            List of new unique insights
        """
        try:
            logger.info(f"Generating {count} additional insights with focus areas: {focus_areas}")
            
            # Prepare the data for analysis
            formatted_data = self._format_kpi_data_for_analysis(kpi_data)
            
            # Generate additional insights with different approach
            additional_insights = self._generate_additional_insights_with_focus(
                formatted_data, existing_insights, positive_examples, count, focus_areas
            )
            
            # Filter out any duplicates or similar insights
            unique_insights = self._filter_unique_insights(additional_insights, existing_insights)
            
            logger.info(f"Generated {len(unique_insights)} unique additional insights")
            return unique_insights[:count]  # Return only requested count
            
        except Exception as e:
            logger.error(f"Error generating additional AI insights: {str(e)}")
            raise
    
    def _generate_additional_insights_with_focus(self, formatted_data: str, existing_insights: List[str], 
                                               positive_examples: List[str], count: int, 
                                               focus_areas: List[str]) -> List[str]:
        """Generate insights with specific focus areas to ensure novelty"""
        
        focus_prompts = {
            'operational_efficiency': "Focus on operational efficiency, process optimization, and workflow improvements",
            'predictive_analysis': "Focus on predictive patterns, future trends, and early warning indicators",
            'strategic_recommendations': "Focus on strategic decisions, leadership actions, and organizational changes",
            'compliance_analysis': "Focus on regulatory compliance, policy adherence, and audit findings",
            'behavioral_patterns': "Focus on human behavior patterns, training needs, and cultural aspects",
            'systemic_issues': "Focus on systemic problems, root causes, and process breakdowns",
            'technical_analysis': "Focus on technical aspects, equipment performance, and methodology effectiveness",
            'temporal_patterns': "Focus on time-based patterns, scheduling, and cyclical trends",
            'maintenance_optimization': "Focus on maintenance strategies, equipment lifecycle, and resource allocation"
        }
        
        # Create focused prompts based on focus areas
        focus_instructions = []
        if focus_areas:
            for area in focus_areas:
                if area in focus_prompts:
                    focus_instructions.append(focus_prompts[area])
        
        focus_text = " AND ".join(focus_instructions) if focus_instructions else "Focus on different analytical perspectives"
        
        # Build the prompt for additional insights
        prompt = f"""
        As a senior safety analyst, analyze this comprehensive safety data and generate {count} NEW and UNIQUE insights that are DIFFERENT from the existing insights.

        SAFETY DATA:
        {formatted_data}

        EXISTING INSIGHTS TO AVOID (DO NOT REPEAT OR PARAPHRASE):
        {chr(10).join([f"- {insight}" for insight in existing_insights])}

        POSITIVE EXAMPLES (USE AS QUALITY REFERENCE):
        {chr(10).join([f"- {example}" for example in positive_examples])}

        FOCUS REQUIREMENTS:
        {focus_text}

        GENERATION REQUIREMENTS:
        1. Generate exactly {count} insights that are COMPLETELY DIFFERENT from existing ones
        2. Each insight must provide NEW information or perspective
        3. Use different analytical angles: {', '.join(focus_areas) if focus_areas else 'various perspectives'}
        4. Avoid repetition or paraphrasing of existing insights
        5. Be specific, actionable, and data-driven
        6. Each insight should be 1-2 sentences maximum
        7. Focus on practical implications and recommendations

        FORMAT: Return ONLY the insights as a numbered list (1., 2., 3., etc.) without any additional text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a senior safety analyst expert at generating unique, actionable insights from safety data. Always provide fresh perspectives that complement existing analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.8,  # Higher temperature for more creative/diverse insights
                top_p=0.9
            )
            
            insights_text = response.choices[0].message.content.strip()
            
            # Parse the insights from the response
            insights = []
            for line in insights_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    insight = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('- ').strip()
                    if insight and len(insight) > 20:  # Filter out very short responses
                        insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI for additional insights: {str(e)}")
            raise
    
    def _filter_unique_insights(self, new_insights: List[str], existing_insights: List[str]) -> List[str]:
        """Filter out insights that are too similar to existing ones"""
        unique_insights = []
        
        for new_insight in new_insights:
            is_unique = True
            new_words = set(new_insight.lower().split())
            
            for existing_insight in existing_insights:
                existing_words = set(existing_insight.lower().split())
                
                # Calculate word overlap - if more than 50% overlap, consider it similar
                overlap = len(new_words.intersection(existing_words))
                similarity_ratio = overlap / max(len(new_words), len(existing_words), 1)
                
                if similarity_ratio > 0.5:  # More than 50% word overlap
                    is_unique = False
                    break
            
            if is_unique:
                unique_insights.append(new_insight)
        
        return unique_insights
    
    def _format_kpi_data_for_analysis(self, kpi_data: Dict[str, Any]) -> str:
        """Format KPI data into a structured string for AI analysis"""
        
        def convert_decimals(obj):
            """Recursively convert Decimal objects to float"""
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            else:
                return obj
        
        def safe_slice(data, count):
            """Safely slice data, ensuring it's a list first"""
            if not data:
                return []
            if isinstance(data, list):
                return data[:count]
            elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                return list(data)[:count]
            else:
                return [data] if data else []
        
        def safe_json_dumps(data, count=None):
            """Safely convert data to JSON string"""
            try:
                if count is not None:
                    data = safe_slice(data, count)
                if not data:
                    return 'No data'
                return json.dumps(data, cls=DecimalEncoder, indent=2)
            except Exception as e:
                logger.warning(f"Error converting data to JSON: {e}")
                return f'Data available but serialization error: {str(e)}'
        
        # Convert all Decimal objects to floats
        clean_kpi_data = convert_decimals(kpi_data)
        
        # Extract key metrics with safe defaults
        core_metrics = {
            "total_unsafe_events": clean_kpi_data.get("number_of_unsafe_events", 0),
            "near_misses": clean_kpi_data.get("near_misses", 0),
            "nogo_violations": clean_kpi_data.get("number_of_nogo_violations", 0),
        }
        
        # Format data safely
        monthly_trends = safe_json_dumps(clean_kpi_data.get("monthly_unsafe_events_trend", []), 6)
        branch_data = safe_json_dumps(clean_kpi_data.get("unsafe_events_by_branch", []), 5)
        region_data = safe_json_dumps(clean_kpi_data.get("unsafe_events_by_region", []), 5)
        unsafe_behaviors = safe_json_dumps(clean_kpi_data.get("common_unsafe_behaviors", []), 5)
        work_hours_lost = safe_json_dumps(clean_kpi_data.get("work_hours_lost", []), 3)
        action_compliance = safe_json_dumps(clean_kpi_data.get("action_creation_and_compliance", []), 3)
        time_patterns = safe_json_dumps(clean_kpi_data.get("unsafe_events_by_time_of_day", []), 5)
        risk_data = safe_json_dumps(clean_kpi_data.get("at_risk_regions", []), 3)
        
        formatted_summary = f"""
        COMPREHENSIVE SAFETY KPI ANALYSIS DATA:
        
        CORE SAFETY METRICS:
        - Total Unsafe Events: {core_metrics['total_unsafe_events']}
        - Near Misses: {core_metrics['near_misses']}
        - NOGO Violations: {core_metrics['nogo_violations']}
        
        MONTHLY TRENDS: {monthly_trends}
        
        TOP BRANCHES BY INCIDENTS: {branch_data}
        
        REGIONAL BREAKDOWN: {region_data}
        
        UNSAFE BEHAVIORS/CONDITIONS: {unsafe_behaviors}
        
        WORK HOURS IMPACT: {work_hours_lost}
        
        ACTION COMPLIANCE: {action_compliance}
        
        TIME-BASED PATTERNS: {time_patterns}
        
        HIGH-RISK AREAS: {risk_data}
        """
        
        return formatted_summary
    
    def _generate_comprehensive_insights(self, data: str) -> List[str]:
        """Generate comprehensive insights combining all aspects"""
        
        prompt = f"""
        Analyze the following safety KPI data and provide exactly 10 concise, actionable insights in bullet point format.
        
        CRITICAL REQUIREMENTS:
        - Each bullet point must be exactly 15-20 words
        - Must include specific branch analysis and branch-level recommendations
        - Focus on actionable insights with specific data points
        - Include geographic patterns, branch performance, and operational recommendations
        
        Key areas to cover:
        1. Branch-specific incident analysis and performance comparison
        2. Geographic risk patterns and regional safety performance
        3. Trend analysis with specific time patterns and seasonal data
        4. Operational efficiency and work hours impact analysis
        5. NOGO violations and compliance gaps by location
        6. Near miss reporting patterns and safety culture indicators
        7. High-risk time periods and shift-based incident patterns
        8. Action item compliance and closure rates by branch
        9. Resource allocation recommendations based on incident concentration
        10. Priority safety interventions with measurable outcomes
        
        Data:
        {data}
        
        Provide exactly 10 insights as bullet points starting with '•'. Each bullet point must be 15-20 words and include specific branch names, numbers, or percentages when available.
        
        Response format: Only bullet points, no introduction text or categories.
        """
        
        return self._call_openai_for_insights(prompt)
    
    def _call_openai_for_insights(self, prompt: str) -> List[str]:
        """Make API call to Azure OpenAI and process response"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior safety analytics expert with deep expertise in EI Tech workplace safety data analysis, risk management, and operational excellence. Provide comprehensive, strategic insights that combine multiple data points into actionable business intelligence."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse bullet points from response
            bullet_points = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    # Clean up bullet point formatting
                    clean_point = line.lstrip('•-* ').strip()
                    if clean_point:
                        bullet_points.append(clean_point)
            
            # Ensure we have exactly 10 insights
            if len(bullet_points) > 10:
                bullet_points = bullet_points[:10]
            elif len(bullet_points) < 10:
                # If we got fewer than 10, pad with a note
                while len(bullet_points) < 10:
                    bullet_points.append("Additional analysis requires more comprehensive data for deeper insights.")
            
            return bullet_points
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {str(e)}")
            return [f"Error generating insights: {str(e)}"]
    
    def generate_executive_summary(self, kpi_data: Dict[str, Any]) -> str:
        """Generate a concise executive summary of the safety performance"""
        
        formatted_data = self._format_kpi_data_for_analysis(kpi_data)
        
        prompt = f"""
        Based on the following safety KPI data, provide a concise executive summary (2-3 paragraphs) 
        highlighting the most critical safety performance points for leadership review.
        
        Data:
        {formatted_data}
        
        Focus on:
        - Overall safety performance status
        - Most critical areas of concern
        - Key achievements or improvements
        - Priority areas requiring immediate attention
        
        Keep it concise and executive-level appropriate.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a safety analytics expert creating executive summaries for senior leadership. Be concise, factual, and highlight critical information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return f"Error generating executive summary: {str(e)}" 