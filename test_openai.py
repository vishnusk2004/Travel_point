#!/usr/bin/env python
"""
Test script to verify OpenAI API integration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelpoints.settings')
django.setup()

from articles.services import rewrite_article_content
from articles.models import Article

def test_openai_integration():
    """Test OpenAI integration with a sample article"""
    
    # Get a sample article
    article = Article.objects.filter(content__isnull=False).exclude(content='').first()
    
    if not article:
        print("No articles found with content to test.")
        return False
    
    print(f"Testing with article: {article.title}")
    print(f"Content length: {len(article.content)} characters")
    print("-" * 50)
    
    # Test the AI content generation
    try:
        result = rewrite_article_content(article.content[:2000])  # Use first 2000 chars for testing
        
        if result:
            print("✅ OpenAI integration successful!")
            print(f"Generated content type: {type(result)}")
            print(f"Keys in result: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            if isinstance(result, dict):
                if 'summary' in result:
                    print(f"Summary: {result['summary'][:100]}...")
                if 'key_points' in result:
                    print(f"Key points: {len(result['key_points'])} found")
                if 'sections' in result:
                    print(f"Sections: {len(result['sections'])} found")
            
            return True
        else:
            print("❌ OpenAI integration failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenAI integration: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API Integration...")
    print("=" * 50)
    
    success = test_openai_integration()
    
    if success:
        print("\n✅ Test passed! You can now run the management command.")
        print("Run: python manage.py generate_ai_content --limit 1")
    else:
        print("\n❌ Test failed! Please check your OpenAI API key.")
        print("Make sure to set OPENAI_API_KEY in your .env file") 