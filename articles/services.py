import os
from dotenv import load_dotenv
import openai
from django.conf import settings
from .schemas import ArticleContent, ArticleSection
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_mock_structured_content(content: str) -> dict:
    """
    Create mock structured content for demonstration when OpenAI API is not available.
    """
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    
    # Create a simple summary from the first paragraph
    summary = paragraphs[0][:200] + "..." if len(paragraphs[0]) > 200 else paragraphs[0]
    
    # Create some key points from the content
    key_points = []
    for i, para in enumerate(paragraphs[:3]):
        if len(para) > 50:
            key_points.append(para[:100] + "...")
    
    # Create sections
    sections = []
    
    # Add a main heading
    sections.append({
        "type": "heading",
        "content": "Article Overview",
        "level": 1
    })
    
    # Add paragraphs as sections
    for i, para in enumerate(paragraphs[:5]):  # Limit to first 5 paragraphs
        if para:
            sections.append({
                "type": "paragraph",
                "content": para
            })
    
    # Add a subheading and more content if available
    if len(paragraphs) > 5:
        sections.append({
            "type": "subheading",
            "content": "Additional Information",
            "level": 2
        })
        
        for para in paragraphs[5:8]:  # Add a few more paragraphs
            if para:
                sections.append({
                    "type": "paragraph",
                    "content": para
                })
    
    return {
        "title": "Structured Article Content",
        "summary": summary,
        "key_points": key_points,
        "sections": sections
    }

def rewrite_article_content(content: str) -> dict:
    """
    Rewrite article content using OpenAI's GPT model and return structured content as a dictionary.
    """
    try:
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key or api_key == 'your_openai_api_key_here':
            logger.warning("OpenAI API key not found. Using mock structured content for demonstration.")
            return create_mock_structured_content(content)
            
        client = openai.OpenAI(api_key=api_key)
        
        # Truncate content if it's too long (OpenAI has token limits)
        max_content_length = 8000  # Approximate token limit
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""Please rewrite and structure the following article content into a well-formatted JSON structure.
        The content should be organized into sections with proper headings and paragraphs.
        Include a summary and key points if relevant.

        Important formatting guidelines:
        1. Each paragraph should be a separate section
        2. Use clear headings to break up content
        3. Include subheadings for better organization
        4. Add relevant quotes where appropriate
        5. Ensure each section has proper spacing and separation

        Original content:
        {content}

        Return the response in the following JSON format:
        {{
            "title": "Main title of the article",
            "summary": "A brief summary of the article",
            "key_points": ["Key point 1", "Key point 2", ...],
            "sections": [
                {{
                    "type": "heading",
                    "content": "Main heading",
                    "level": 1
                }},
                {{
                    "type": "paragraph",
                    "content": "First paragraph content"
                }},
                {{
                    "type": "paragraph",
                    "content": "Second paragraph content"
                }},
                {{
                    "type": "subheading",
                    "content": "Subheading",
                    "level": 2
                }},
                {{
                    "type": "paragraph",
                    "content": "Another paragraph"
                }},
                {{
                    "type": "quote",
                    "content": "Important quote or highlight"
                }},
                ...
            ]
        }}

        Ensure the content is well-structured, engaging, and maintains the original meaning while being more readable.
        Each paragraph should be a separate section to ensure proper spacing and readability.
        """

        logger.info("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional content editor who specializes in structuring and formatting articles."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            max_tokens=4000
        )

        # Parse the response into our Pydantic model
        content_json = response.choices[0].message.content
        logger.info("Received response from OpenAI API")
        
        # Parse and validate the JSON response
        try:
            article_content = ArticleContent.model_validate_json(content_json)
            # Convert to dictionary for database storage
            result = article_content.model_dump()
            logger.info("Successfully processed AI response")
            return result
        except Exception as validation_error:
            logger.error(f"Error validating AI response: {validation_error}")
            # Try to parse as JSON and return raw structure
            try:
                raw_json = json.loads(content_json)
                logger.info("Returning raw JSON structure")
                return raw_json
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response as JSON")
                return create_mock_structured_content(content)

    except openai.AuthenticationError:
        logger.error("OpenAI authentication failed. Please check your API key.")
        return create_mock_structured_content(content)
    except openai.RateLimitError:
        logger.error("OpenAI rate limit exceeded. Please try again later.")
        return create_mock_structured_content(content)
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return create_mock_structured_content(content)
    except Exception as e:
        logger.error(f"Error in rewrite_article_content: {str(e)}")
        return create_mock_structured_content(content) 