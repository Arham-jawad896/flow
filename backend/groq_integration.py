import os
import json
import logging
from typing import Dict, Any, Optional, List
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)

class GroqLLMService:
    """Service for integrating with GroqCloud LLM for data analysis and insights."""
    
    def __init__(self):
        self.client = None
        if settings.groq_api_key:
            try:
                self.client = Groq(api_key=settings.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {str(e)}")
        else:
            logger.warning("Groq API key not provided, LLM features disabled")
    
    def is_available(self) -> bool:
        """Check if Groq service is available."""
        return self.client is not None
    
    def analyze_dataset_summary(self, dataset_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset and provide insights using LLM."""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Groq service not available',
                'insights': []
            }
        
        try:
            # Prepare dataset summary for LLM
            summary_text = self._prepare_dataset_summary(dataset_info)
            
            # Create prompt for data analysis
            prompt = f"""
            As a data science expert, analyze the following dataset and provide insights:
            
            {summary_text}
            
            Please provide:
            1. Data quality assessment
            2. Potential issues or patterns
            3. Recommendations for preprocessing
            4. Suggested next steps for analysis
            
            Format your response as a JSON object with the following structure:
            {{
                "data_quality": {{
                    "score": "score out of 10",
                    "issues": ["list of issues"],
                    "strengths": ["list of strengths"]
                }},
                "insights": [
                    {{
                        "type": "pattern|issue|recommendation",
                        "title": "Brief title",
                        "description": "Detailed description",
                        "priority": "high|medium|low"
                    }}
                ],
                "recommendations": [
                    {{
                        "action": "specific action to take",
                        "reason": "why this action is recommended",
                        "impact": "expected impact"
                    }}
                ]
            }}
            """
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data science expert specializing in dataset analysis and preprocessing recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Find JSON in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    insights = json.loads(json_text)
                else:
                    # Fallback: create structured response from text
                    insights = self._parse_text_response(response_text)
            except json.JSONDecodeError:
                insights = self._parse_text_response(response_text)
            
            return {
                'success': True,
                'insights': insights,
                'raw_response': response_text
            }
            
        except Exception as e:
            logger.error(f"Error in dataset analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'insights': []
            }
    
    def generate_preprocessing_recommendations(
        self, 
        dataset_info: Dict[str, Any], 
        current_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate preprocessing recommendations based on dataset characteristics."""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Groq service not available',
                'recommendations': {}
            }
        
        try:
            # Prepare dataset info
            summary_text = self._prepare_dataset_summary(dataset_info)
            
            # Create prompt for preprocessing recommendations
            prompt = f"""
            As a machine learning engineer, analyze this dataset and recommend optimal preprocessing settings:
            
            {summary_text}
            
            Current preprocessing options (if any):
            {json.dumps(current_options, indent=2) if current_options else "None specified"}
            
            Please recommend the best preprocessing configuration for this dataset. Consider:
            - Data types and distributions
            - Missing values patterns
            - Categorical vs numerical features
            - Potential outliers
            - Target variable characteristics (if identifiable)
            
            Respond with a JSON object:
            {{
                "scaling_method": "minmax|standard|robust",
                "missing_value_strategy": "mean|median|mode",
                "outlier_removal": true/false,
                "data_augmentation": true/false,
                "feature_engineering": true/false,
                "train_test_split": 0.8,
                "reasoning": {{
                    "scaling_method": "explanation for scaling choice",
                    "missing_value_strategy": "explanation for imputation choice",
                    "outlier_removal": "explanation for outlier handling",
                    "other_recommendations": ["additional recommendations"]
                }}
            }}
            """
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a machine learning engineer with expertise in data preprocessing and feature engineering."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    recommendations = json.loads(json_text)
                else:
                    recommendations = self._create_default_recommendations()
            except json.JSONDecodeError:
                recommendations = self._create_default_recommendations()
            
            return {
                'success': True,
                'recommendations': recommendations,
                'raw_response': response_text
            }
            
        except Exception as e:
            logger.error(f"Error generating preprocessing recommendations: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': self._create_default_recommendations()
            }
    
    def explain_preprocessing_steps(self, preprocessing_log: List[str]) -> Dict[str, Any]:
        """Explain preprocessing steps in user-friendly terms."""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Groq service not available',
                'explanation': 'Preprocessing completed successfully'
            }
        
        try:
            log_text = "\n".join(preprocessing_log)
            
            prompt = f"""
            Explain the following data preprocessing steps in simple, user-friendly terms:
            
            {log_text}
            
            Provide a clear explanation that a non-technical user can understand, including:
            1. What each step accomplished
            2. Why it was necessary
            3. How it improves the data quality
            
            Format as a JSON object:
            {{
                "summary": "Brief overview of what was done",
                "steps": [
                    {{
                        "step": "step name",
                        "description": "what it does",
                        "benefit": "why it's important"
                    }}
                ],
                "overall_impact": "how the preprocessing improves the dataset"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data science educator who explains complex concepts in simple terms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    explanation = json.loads(json_text)
                else:
                    explanation = {
                        "summary": "Data preprocessing completed successfully",
                        "steps": [{"step": "Processing", "description": "Data was cleaned and prepared", "benefit": "Improved data quality"}],
                        "overall_impact": "Your data is now ready for analysis"
                    }
            except json.JSONDecodeError:
                explanation = {
                    "summary": "Data preprocessing completed successfully",
                    "steps": [{"step": "Processing", "description": "Data was cleaned and prepared", "benefit": "Improved data quality"}],
                    "overall_impact": "Your data is now ready for analysis"
                }
            
            return {
                'success': True,
                'explanation': explanation,
                'raw_response': response_text
            }
            
        except Exception as e:
            logger.error(f"Error explaining preprocessing steps: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'explanation': {
                    "summary": "Data preprocessing completed successfully",
                    "steps": [{"step": "Processing", "description": "Data was cleaned and prepared", "benefit": "Improved data quality"}],
                    "overall_impact": "Your data is now ready for analysis"
                }
            }
    
    def _prepare_dataset_summary(self, dataset_info: Dict[str, Any]) -> str:
        """Prepare dataset information for LLM analysis."""
        summary = f"""
        Dataset Information:
        - Name: {dataset_info.get('name', 'Unknown')}
        - File Type: {dataset_info.get('file_type', 'Unknown')}
        - File Size: {dataset_info.get('file_size', 0)} bytes
        - Rows: {dataset_info.get('rows_count', 'Unknown')}
        - Columns: {dataset_info.get('columns_count', 'Unknown')}
        - Preprocessing Status: {dataset_info.get('preprocessing_status', 'Unknown')}
        """
        
        if 'preprocessing_log' in dataset_info and dataset_info['preprocessing_log']:
            summary += f"\nPreprocessing Log:\n{dataset_info['preprocessing_log']}"
        
        return summary
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        return {
            "data_quality": {
                "score": "8",
                "issues": ["Unable to parse detailed analysis"],
                "strengths": ["Dataset appears to be processed"]
            },
            "insights": [
                {
                    "type": "recommendation",
                    "title": "LLM Analysis",
                    "description": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    "priority": "medium"
                }
            ],
            "recommendations": [
                {
                    "action": "Review the analysis above",
                    "reason": "LLM provided insights about your dataset",
                    "impact": "Better understanding of data characteristics"
                }
            ]
        }
    
    def _create_default_recommendations(self) -> Dict[str, Any]:
        """Create default preprocessing recommendations."""
        return {
            "scaling_method": "minmax",
            "missing_value_strategy": "mean",
            "outlier_removal": False,
            "data_augmentation": False,
            "feature_engineering": False,
            "train_test_split": 0.8,
            "reasoning": {
                "scaling_method": "MinMax scaling is generally safe for most datasets",
                "missing_value_strategy": "Mean imputation works well for numerical data",
                "outlier_removal": "Conservative approach - keep outliers unless clearly problematic",
                "other_recommendations": ["Start with basic preprocessing and iterate based on results"]
            }
        }

# Global instance
groq_service = GroqLLMService()
