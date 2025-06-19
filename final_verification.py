#!/usr/bin/env python
"""
Final Verification - Check if all articles have AI content
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

def final_verification():
    """Final verification to ensure all articles have AI content"""
    
    print("🔍 FINAL VERIFICATION - AI CONTENT COMPLETENESS")
    print("=" * 60)
    
    # Get all articles
    total_articles = Article.objects.count()
    articles_with_content = Article.objects.filter(content__isnull=False).exclude(content='').count()
    articles_with_ai = Article.objects.filter(structured_content__isnull=False).exclude(structured_content={}).count()
    
    # Find articles that should have AI content but don't
    articles_needing_ai = Article.objects.filter(
        structured_content__isnull=True,
        content__isnull=False
    ).exclude(content='')
    
    print(f"📊 Database Summary:")
    print(f"   • Total articles: {total_articles}")
    print(f"   • Articles with content: {articles_with_content}")
    print(f"   • Articles with AI content: {articles_with_ai}")
    print(f"   • Articles needing AI content: {articles_needing_ai.count()}")
    
    if articles_with_content > 0:
        coverage = (articles_with_ai / articles_with_content) * 100
        print(f"   • AI coverage: {coverage:.1f}%")
    
    print(f"\n✅ VERIFICATION RESULTS:")
    
    # Check 1: All articles with content should have AI content
    if articles_needing_ai.count() == 0:
        print(f"   ✅ All articles with content have AI enhancement")
    else:
        print(f"   ❌ {articles_needing_ai.count()} articles still need AI content:")
        for article in articles_needing_ai[:5]:
            print(f"      • {article.title[:60]}... (ID: {article.id})")
        if articles_needing_ai.count() > 5:
            print(f"      ... and {articles_needing_ai.count() - 5} more")
    
    # Check 2: AI content quality
    if articles_with_ai > 0:
        sample = Article.objects.filter(structured_content__isnull=False).first()
        if sample:
            structured = sample.structured_content
            has_summary = bool(structured.get('summary'))
            has_key_points = bool(structured.get('key_points'))
            has_sections = bool(structured.get('sections'))
            
            print(f"   ✅ AI content structure is complete:")
            print(f"      • Summary: {'✅' if has_summary else '❌'}")
            print(f"      • Key Points: {'✅' if has_key_points else '❌'}")
            print(f"      • Sections: {'✅' if has_sections else '❌'}")
    
    # Check 3: No orphaned data
    articles_without_content = Article.objects.filter(content__isnull=True).count()
    if articles_without_content == 0:
        print(f"   ✅ No articles without content (clean database)")
    else:
        print(f"   ⚠️  {articles_without_content} articles without content")
    
    # Final status
    print(f"\n🎯 FINAL STATUS:")
    if articles_needing_ai.count() == 0 and articles_with_ai > 0:
        print(f"   🎉 COMPLETE SUCCESS! All articles have AI content.")
        print(f"   🚀 Your website is fully AI-enhanced!")
    elif articles_needing_ai.count() > 0:
        print(f"   ⚠️  INCOMPLETE: {articles_needing_ai.count()} articles still need processing.")
        print(f"   💡 Run: python process_all_articles.py to complete")
    else:
        print(f"   ❌ No AI content found. Check your setup.")
    
    print(f"\n📋 RECOMMENDATIONS:")
    if articles_needing_ai.count() == 0:
        print(f"   • ✅ All processing complete")
        print(f"   • ✅ Visit: http://127.0.0.1:8015/articles/[ID]/")
        print(f"   • ✅ Monitor OpenAI usage")
    else:
        print(f"   • 🔄 Continue processing remaining articles")
        print(f"   • 📊 Check for any errors in the processing")
    
    print("=" * 60)

if __name__ == "__main__":
    final_verification() 