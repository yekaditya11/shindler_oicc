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
        Generate AI-powered analytical insights from KPI data focused on event analysis
        
        Args:
            kpi_data: Dictionary containing KPI metrics from EI Tech system
            
        Returns:
            Dictionary containing comprehensive analytical insights with sentiment analysis
            focused on event patterns, correlations, and statistical observations
        """
        try:
            logger.info("Starting AI insights generation with sentiment analysis")
            
            # Prepare the data for analysis
            formatted_data = self._format_kpi_data_for_analysis(kpi_data)
            
            # Generate comprehensive insights with sentiment
            insights_list = self._generate_comprehensive_insights(formatted_data)
            
            result = {
                "insights": insights_list,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "data_period": f"{kpi_data.get('query_metadata', {}).get('start_date', 'N/A')} to {kpi_data.get('query_metadata', {}).get('end_date', 'N/A')}",
                    "ai_model": self.deployment_name,
                    "total_insights": len(insights_list),
                    "sentiment_enabled": True
                }
            }
            
            logger.info("AI insights generation with sentiment analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            raise
    
    def generate_additional_insights(self, kpi_data: Dict[str, Any], existing_insights: List[str], 
                                   positive_examples: List[str], count: int = 5, 
                                   focus_areas: List[str] = None) -> List[str]:
        """
        Generate additional analytical insights focused on event patterns that are different from existing ones
        
        Args:
            kpi_data: Dictionary containing KPI metrics
            existing_insights: List of already generated insights to avoid duplicates
            positive_examples: List of insights that received positive feedback
            count: Number of new insights to generate
            focus_areas: List of specific analytical areas to focus on
            
        Returns:
            List of new unique analytical insights with sentiment analysis focused on event patterns
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
            
            logger.info(f"Generated {len(unique_insights)} unique additional insights with sentiment")
            return unique_insights[:count]  # Return only requested count
            
        except Exception as e:
            logger.error(f"Error generating additional AI insights: {str(e)}")
            raise
    
    def _generate_additional_insights_with_focus(self, formatted_data: str, existing_insights: List[str], 
                                               positive_examples: List[str], count: int, 
                                               focus_areas: List[str]) -> List[Dict[str, str]]:
        """Generate insights with specific focus areas to ensure novelty"""
        
        focus_prompts = {
            'operational_efficiency': "Focus on operational patterns, process performance correlations, and workflow bottleneck analysis",
            'predictive_analysis': "Focus on predictive indicators, leading metrics identification, and statistical forecasting patterns",
            'strategic_recommendations': "Focus on organizational performance patterns, leadership impact analysis, and structural correlation insights",
            'compliance_analysis': "Focus on compliance pattern analysis, regulatory deviation trends, and systematic adherence gaps",
            'behavioral_patterns': "Focus on human behavior correlations, cultural indicators, and performance pattern analysis",
            'systemic_issues': "Focus on system failure patterns, root cause correlations, and process breakdown analysis",
            'technical_analysis': "Focus on equipment performance patterns, technical failure correlations, and methodology effectiveness analysis",
            'temporal_patterns': "Focus on time-based correlations, cyclical pattern analysis, and scheduling impact patterns",
            'maintenance_optimization': "Focus on maintenance pattern analysis, equipment lifecycle correlations, and resource utilization patterns"
        }
        
        # Create focused prompts based on focus areas
        focus_instructions = []
        if focus_areas:
            for area in focus_areas:
                if area in focus_prompts:
                    focus_instructions.append(focus_prompts[area])
        
        focus_text = " AND ".join(focus_instructions) if focus_instructions else "Focus on different analytical perspectives"
        
        # Build the prompt for additional insights with sentiment
        prompt = f"""
        You are an AI assistant working within the Safety and Health Management domain. Your role is to provide support to senior-level safety professionals, including the Safety Head and VP of Safety. The primary goal is to ensure the organization is consistently compliant with external safety regulations such as OSHA, ISO 45001, and local safety laws. You will assist in tracking and updating internal safety protocols, ensuring they align with regulatory changes and industry best practices.
        Your focus includes overseeing the implementation of safety standards across various departments, such as workplace safety, machinery handling, fire safety, and employee well-being. You will assist in preparing for and conducting safety inspections, ensuring that the organization is ready for both internal and external audits. The safety leaders rely on you to stay informed on evolving safety requirements and help in the continuous improvement of safety programs. Your role includes proactively identifying high-risk locations and uncovering commonly occurring unsafe conditions and behaviors, ensuring these are promptly brought to the attention of the safety leaders responsible for corrective action.
        The goal is to minimize safety risks by proactively identifying potential hazards, maintaining compliance, and driving improvements in safety practices across the organization. You support safety leadership in ensuring a culture of safety is deeply embedded in every department and aspect of the organization's operations.
        analyze this comprehensive safety data and generate {count} NEW and UNIQUE analytical insights that are DIFFERENT from the existing insights.
        Focus on EVENT ANALYSIS and PATTERN IDENTIFICATION rather than recommendations.

        SAFETY DATA:
        {formatted_data}

        EXISTING INSIGHTS TO AVOID (DO NOT REPEAT OR PARAPHRASE):
        {chr(10).join([f"- {insight}" for insight in existing_insights])}

        POSITIVE EXAMPLES (USE AS QUALITY REFERENCE):
        {chr(10).join([f"- {example}" for example in positive_examples])}

        FOCUS REQUIREMENTS:
        {focus_text}

        GENERATION REQUIREMENTS:
        1. Generate exactly {count} analytical insights that are COMPLETELY DIFFERENT from existing ones
        2. Each insight must provide NEW analytical observations about event patterns or correlations
        3. Focus on WHAT IS HAPPENING and WHY, not what should be done about it
        4. Avoid repetition or paraphrasing of existing insights
        5. Be specific, data-driven, and focused on event analysis
        6. Each insight should be 1-2 sentences maximum
        7. Focus on statistical patterns, correlations, and event characteristics
        8. CLASSIFY each insight's sentiment as 'positive', 'negative', or 'neutral'

        SENTIMENT CLASSIFICATION GUIDELINES:
        - POSITIVE: Improvements, achievements, good performance, declining risks, successful interventions
        - NEGATIVE: Deteriorating conditions, high risks, compliance failures, safety concerns, incidents increasing
        - NEUTRAL: Status updates, procedural information, data observations without clear positive/negative impact

        ANALYTICAL FOCUS (NO RECOMMENDATIONS):
        - Event frequency patterns and their statistical significance
        - Correlation analysis between different incident types and factors
        - Temporal and geographic clustering patterns in event data
        - Performance indicators and their relationship to incident rates
        - Cultural and behavioral pattern analysis from event reporting

        Response format: Return EXACTLY {count} insights in this JSON format:
        [
          {{"text": "analytical insight about event patterns here", "sentiment": "positive|negative|neutral"}},
          {{"text": "analytical insight about event patterns here", "sentiment": "positive|negative|neutral"}},
          ...
        ]

        Provide ONLY the JSON array, no additional text or formatting.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a senior safety analyst expert at generating unique, analytical insights from safety data with accurate sentiment classification. Focus on event pattern analysis and statistical observations rather than recommendations. Always provide fresh analytical perspectives that complement existing analysis. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.8,  # Higher temperature for more creative/diverse insights
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the structured insights from the response
            try:
                insights_json = json.loads(content)
                if isinstance(insights_json, list) and all(isinstance(item, dict) for item in insights_json):
                    # Validate and structure the insights
                    structured_insights = []
                    for item in insights_json:
                        if 'text' in item and 'sentiment' in item:
                            sentiment = item['sentiment'].lower()
                            if sentiment not in ['positive', 'negative', 'neutral']:
                                sentiment = 'neutral'
                            
                            structured_insights.append({
                                'text': item['text'],
                                'sentiment': sentiment
                            })
                        elif isinstance(item, str):
                            structured_insights.append({
                                'text': item,
                                'sentiment': 'neutral'
                            })
                    
                    return structured_insights
                else:
                    # Fallback to text parsing
                    return self._parse_additional_insights_fallback(content, count)
                    
            except json.JSONDecodeError:
                # Fallback to text parsing
                return self._parse_additional_insights_fallback(content, count)
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI for additional insights: {str(e)}")
            raise
    
    def _parse_additional_insights_fallback(self, content: str, count: int) -> List[Dict[str, str]]:
        """Parse additional insights from non-JSON response"""
        insights = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering and clean up
                insight = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('- ').strip()
                if insight and len(insight) > 20:  # Filter out very short responses
                    insights.append({
                        'text': insight,
                        'sentiment': 'neutral'  # Default sentiment when parsing fails
                    })
        
        return insights[:count]
    
    def _filter_unique_insights(self, new_insights: List[Dict[str, str]], existing_insights: List[str]) -> List[Dict[str, str]]:
        """Filter out insights that are too similar to existing ones"""
        unique_insights = []
        
        for new_insight in new_insights:
            is_unique = True
            new_text = new_insight.get('text', '')
            new_words = set(new_text.lower().split())
            
            for existing_insight in existing_insights:
                # Handle both string and dict formats for existing insights
                existing_text = existing_insight if isinstance(existing_insight, str) else existing_insight.get('text', '')
                existing_words = set(existing_text.lower().split())
                
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
        
        # Determine data source type and extract metrics accordingly
        if "total_events" in clean_kpi_data:
            # NI_TCT data structure
            total_events_data = clean_kpi_data.get("total_events", {})
            events_by_type = clean_kpi_data.get("events_by_type", [])
            near_miss_count = 0
            for event_type in events_by_type:
                if "near miss" in str(event_type.get("type_of_unsafe_event", "")).lower():
                    near_miss_count = event_type.get("event_count", 0)
                    break
            
            nogo_data = clean_kpi_data.get("nogo_violations", {})
            
            core_metrics = {
                "total_unsafe_events": total_events_data.get("total_events", 0),
                "near_misses": near_miss_count,
                "nogo_violations": nogo_data.get("events_with_nogo_violations", 0),
            }
            
            # NI_TCT specific data extraction
            monthly_trends = safe_json_dumps(clean_kpi_data.get("events_monthly", []), 6)
            branch_data = safe_json_dumps(clean_kpi_data.get("branch_distribution", []), 5)
            region_data = safe_json_dumps(clean_kpi_data.get("regional_distribution", []), 5)
            unsafe_behaviors = safe_json_dumps(events_by_type, 5)
            work_hours_lost = safe_json_dumps(clean_kpi_data.get("work_stoppage_duration", []), 3)
            action_compliance = safe_json_dumps(clean_kpi_data.get("high_risk_response_effectiveness", []), 3)
            time_patterns = safe_json_dumps(clean_kpi_data.get("incidents_by_time_of_day", []), 5)
            risk_data = safe_json_dumps(clean_kpi_data.get("repeat_location_analysis", []), 3)
            
        else:
            # EI Tech data structure (original)
            core_metrics = {
                "total_unsafe_events": clean_kpi_data.get("number_of_unsafe_events", 0),
                "near_misses": clean_kpi_data.get("near_misses", 0),
                "nogo_violations": clean_kpi_data.get("number_of_nogo_violations", 0),
            }
            
            # EI Tech specific data extraction
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
        Analyze the following safety KPI data and provide exactly 5 concise, analytical insights with sentiment analysis.
        Focus on EVENT ANALYSIS and IN-DEPTH UNDERSTANDING rather than recommendations.
        
        CRITICAL REQUIREMENTS:
        - Each insight must be exactly 15-25 words
        - Focus on WHAT IS HAPPENING and WHY, not what to do about it
        - Provide deep analytical observations about event patterns, correlations, and trends
        - Include specific data points and statistical observations
        - CLASSIFY each insight's sentiment as 'positive', 'negative', or 'neutral'
        
        SENTIMENT CLASSIFICATION GUIDELINES:
        - POSITIVE: Improvements, achievements, good performance, declining risks, successful interventions
        - NEGATIVE: Deteriorating conditions, high risks, compliance failures, safety concerns, incidents increasing
        - NEUTRAL: Status updates, procedural information, data observations without clear positive/negative impact
        
        ANALYTICAL FOCUS AREAS (NO RECOMMENDATIONS):
        1. Event frequency patterns and statistical correlations across time periods
        2. Geographic clustering analysis and regional incident concentration patterns
        3. Behavioral pattern analysis and incident type correlations
        4. Temporal trend analysis showing cyclical or seasonal patterns
        5. Severity escalation patterns from near misses to actual incidents
        6. Work disruption impact analysis and productivity correlation patterns
        7. Compliance gap analysis showing systematic non-adherence patterns
        8. Risk manifestation patterns and incident prediction indicators
        9. Organizational safety culture indicators based on reporting patterns
        10. Resource impact analysis showing cost and efficiency correlations
        
        EXAMPLE ANALYTICAL INSIGHTS (NOT RECOMMENDATIONS):
        - "Branch X shows 300% higher incident rate during morning shifts indicating systematic operational stress"
        - "Near miss reporting declined 40% while actual incidents increased, suggesting underreporting culture developing"
        - "NOGO violations cluster in specific equipment categories, indicating design or training gaps"
        
        Data:
        {data}
        
        Response format: Return EXACTLY 10 insights in this JSON format:
        [
          {{"text": "analytical insight about events/patterns here", "sentiment": "positive|negative|neutral"}},
          {{"text": "analytical insight about events/patterns here", "sentiment": "positive|negative|neutral"}},
          ...
        ]
        
        Provide ONLY the JSON array, no additional text or formatting.
        """
        
        return self._call_openai_for_structured_insights(prompt)
    
    def _call_openai_for_structured_insights(self, prompt: str) -> List[Dict[str, str]]:
        """Make API call to Azure OpenAI and process response for structured insights with sentiment"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior safety analytics expert with deep expertise in EI Tech workplace safety data analysis, event pattern recognition, and statistical correlation analysis. Provide comprehensive, analytical insights with accurate sentiment classification that identify patterns, trends, and correlations in safety events. Focus on WHAT IS HAPPENING and WHY rather than recommendations. Always respond with valid JSON format."
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
            
            # Attempt to parse JSON, handle potential errors
            try:
                insights_json = json.loads(content)
                if isinstance(insights_json, list) and all(isinstance(item, dict) for item in insights_json):
                    # Validate that each insight has required fields
                    validated_insights = []
                    for item in insights_json:
                        if 'text' in item and 'sentiment' in item:
                            # Validate sentiment values
                            sentiment = item['sentiment'].lower()
                            if sentiment in ['positive', 'negative', 'neutral']:
                                validated_insights.append({
                                    'text': item['text'],
                                    'sentiment': sentiment
                                })
                            else:
                                # Default to neutral if invalid sentiment
                                validated_insights.append({
                                    'text': item['text'],
                                    'sentiment': 'neutral'
                                })
                        else:
                            # If missing required fields, create a basic insight
                            validated_insights.append({
                                'text': str(item) if isinstance(item, str) else "Analysis requires more comprehensive data for deeper insights.",
                                'sentiment': 'neutral'
                            })
                    
                    # Ensure we have exactly 10 insights
                    if len(validated_insights) > 10:
                        validated_insights = validated_insights[:10]
                    elif len(validated_insights) < 10:
                        # Pad with neutral insights if we got fewer than 10
                        while len(validated_insights) < 10:
                            validated_insights.append({
                                'text': "Additional analysis requires more comprehensive data for deeper insights.",
                                'sentiment': 'neutral'
                            })
                    
                    return validated_insights
                else:
                    logger.warning(f"Azure OpenAI response is not a valid JSON list of insights: {content}")
                    # Return fallback structured insights
                    return self._create_fallback_insights()
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from Azure OpenAI response: {e}")
                # Attempt to extract insights from non-JSON response
                return self._parse_fallback_insights(content)
                
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI for structured insights: {str(e)}")
            return self._create_fallback_insights()
    
    def _create_fallback_insights(self) -> List[Dict[str, str]]:
        """Create fallback insights when API fails"""
        return [
            {"text": "Safety data analysis is currently unavailable. Please try again later.", "sentiment": "neutral"},
            {"text": "System is working to provide comprehensive safety insights.", "sentiment": "neutral"},
            {"text": "Regular monitoring of safety metrics is recommended.", "sentiment": "neutral"},
            {"text": "Safety performance tracking requires consistent data collection.", "sentiment": "neutral"},
            {"text": "Incident reporting systems should be regularly reviewed.", "sentiment": "neutral"},
            {"text": "Training compliance monitoring is essential for safety management.", "sentiment": "neutral"},
            {"text": "Risk assessment procedures should be regularly updated.", "sentiment": "neutral"},
            {"text": "Equipment safety checks require consistent scheduling.", "sentiment": "neutral"},
            {"text": "Safety culture development is an ongoing organizational priority.", "sentiment": "neutral"},
            {"text": "Data quality improvements will enhance future insights.", "sentiment": "neutral"}
        ]
    
    def _parse_fallback_insights(self, content: str) -> List[Dict[str, str]]:
        """Try to parse insights from non-JSON response"""
        insights = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*') or line.startswith('{')):
                # Clean up bullet point formatting
                clean_point = line.lstrip('•-* ').strip()
                if clean_point and not clean_point.startswith('{'):
                    insights.append({
                        'text': clean_point,
                        'sentiment': 'neutral'  # Default to neutral when sentiment can't be determined
                    })
        
        # Ensure we have exactly 10 insights
        if len(insights) > 10:
            insights = insights[:10]
        elif len(insights) < 10:
            insights.extend(self._create_fallback_insights()[:10-len(insights)])
        
        return insights
    
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