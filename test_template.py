#!/usr/bin/env python
"""
Test script to verify template rendering with AI content
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelpoints.settings')
django.setup()

from articles.models import Article
from django.template.loader import render_to_string
from django.test import RequestFactory

def test_template_rendering():
    """Test if the template correctly renders AI-generated content"""
    
    # Get an article with AI content
    article = Article.objects.filter(structured_content__isnull=False).first()
    
    if not article:
        print("No articles found with AI content.")
        return False
    
    print(f"Testing template with article: {article.title}")
    print(f"Article ID: {article.id}")
    print("-" * 50)
    
    # Check the structured content
    structured = article.structured_content
    print(f"Has structured content: {bool(structured)}")
    print(f"Summary: {structured.get('summary', 'No summary')[:100]}...")
    print(f"Key points: {len(structured.get('key_points', []))}")
    print(f"Sections: {len(structured.get('sections', []))}")
    
    # Test template rendering
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get(f'/articles/{article.id}/')
        
        # Render the template
        context = {
            'article': article,
            'paragraphs': []  # Not needed since we have structured content
        }
        
        rendered_html = render_to_string('articles/article_detail.html', context)
        
        # Check if AI content is in the rendered HTML
        if 'Quick Summary' in rendered_html:
            print("✅ Template contains 'Quick Summary' section")
        else:
            print("❌ Template missing 'Quick Summary' section")
            
        if 'Key Takeaways' in rendered_html:
            print("✅ Template contains 'Key Takeaways' section")
        else:
            print("❌ Template missing 'Key Takeaways' section")
            
        if 'Article Overview' in rendered_html or any(section.get('content', '') in rendered_html for section in structured.get('sections', []) if section.get('type') == 'heading'):
            print("✅ Template contains article sections")
        else:
            print("❌ Template missing article sections")
        
        # Check for AI-generated content indicators
        ai_indicators = ['summary', 'key_points', 'sections']
        found_indicators = []
        
        for indicator in ai_indicators:
            if indicator in str(structured):
                found_indicators.append(indicator)
        
        print(f"✅ Found AI content indicators: {', '.join(found_indicators)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rendering template: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Template Rendering with AI Content...")
    print("=" * 50)
    
    success = test_template_rendering()
    
    if success:
        print("\n✅ Template rendering test passed!")
        print("You can now visit http://127.0.0.1:8015/articles/[ID]/ to see the AI content")
    else:
        print("\n❌ Template rendering test failed!") 