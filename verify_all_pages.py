#!/usr/bin/env python
"""
Comprehensive verification script for TravelPoints website
Tests all pages, links, and functionality
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
import requests
from urllib.parse import urljoin

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelpoints.settings')
django.setup()

from articles.models import Article

class WebsiteVerification:
    def __init__(self):
        self.client = Client()
        self.base_url = "http://127.0.0.1:8015"
        self.results = []
        
    def log_result(self, test_name, status, message=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message
        }
        self.results.append(result)
        
        # Print result immediately
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {message}")
        
    def test_page_response(self, url_name, expected_status=200, description=None, **kwargs):
        """Test if a page responds correctly"""
        test_name = description or f"Page: {url_name}"
        
        try:
            if url_name.startswith('http'):
                response = requests.get(url_name, timeout=10)
                url = url_name
            else:
                response = self.client.get(reverse(url_name, kwargs=kwargs))
                url = reverse(url_name, kwargs=kwargs)
            
            if response.status_code == expected_status:
                self.log_result(test_name, "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_result(test_name, "FAIL", f"Expected {expected_status}, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(test_name, "ERROR", f"Exception: {str(e)}")
            return False
    
    def test_all_pages(self):
        """Test all main pages"""
        print("\n" + "="*60)
        print("TESTING ALL PAGES")
        print("="*60)
        
        pages_to_test = [
            ('home', 'Home Page'),
            ('article_list', 'Articles List Page'),
            ('destinations', 'Destinations Page'),
            ('about', 'About Page'),
            ('points_guide', 'Points Guide Page'),
            ('travel_tips', 'Travel Tips Page'),
            ('contact', 'Contact Page'),
            ('privacy_policy', 'Privacy Policy Page'),
            ('terms_of_service', 'Terms of Service Page'),
            ('cookie_policy', 'Cookie Policy Page'),
        ]
        
        for url_name, description in pages_to_test:
            self.test_page_response(url_name, 200, description)
    
    def test_article_detail_pages(self):
        """Test article detail pages"""
        print("\n" + "="*60)
        print("TESTING ARTICLE DETAIL PAGES")
        print("="*60)
        
        articles = Article.objects.all()[:5]  # Test first 5 articles
        
        if not articles:
            self.log_result("Article Detail Pages", "SKIP", "No articles in database")
            return
            
        for article in articles:
            self.test_page_response(
                'article_detail', 
                200, 
                f"Article Detail: {article.title[:50]}...",
                article_id=article.id
            )
    
    def test_navigation_links(self):
        """Test navigation links in base template"""
        print("\n" + "="*60)
        print("TESTING NAVIGATION LINKS")
        print("="*60)
        
        # Test that home page loads and contains navigation links
        try:
            response = self.client.get(reverse('home'))
            content = response.content.decode('utf-8')
            
            # Check for navigation links
            nav_links = [
                'href="{% url \'home\' %}"',
                'href="{% url \'article_list\' %}"',
                'href="{% url \'destinations\' %}"',
                'href="{% url \'about\' %}"',
            ]
            
            for link in nav_links:
                if link in content:
                    self.log_result(f"Nav Link: {link}", "PASS", "Link found in template")
                else:
                    self.log_result(f"Nav Link: {link}", "FAIL", "Link not found in template")
                    
        except Exception as e:
            self.log_result("Navigation Links", "ERROR", f"Exception: {str(e)}")
    
    def test_footer_links(self):
        """Test footer links"""
        print("\n" + "="*60)
        print("TESTING FOOTER LINKS")
        print("="*60)
        
        try:
            response = self.client.get(reverse('home'))
            content = response.content.decode('utf-8')
            
            footer_links = [
                'href="{% url \'points_guide\' %}"',
                'href="{% url \'travel_tips\' %}"',
                'href="{% url \'contact\' %}"',
                'href="{% url \'privacy_policy\' %}"',
                'href="{% url \'terms_of_service\' %}"',
                'href="{% url \'cookie_policy\' %}"',
            ]
            
            for link in footer_links:
                if link in content:
                    self.log_result(f"Footer Link: {link}", "PASS", "Link found in template")
                else:
                    self.log_result(f"Footer Link: {link}", "FAIL", "Link not found in template")
                    
        except Exception as e:
            self.log_result("Footer Links", "ERROR", f"Exception: {str(e)}")
    
    def test_seo_elements(self):
        """Test SEO elements on pages"""
        print("\n" + "="*60)
        print("TESTING SEO ELEMENTS")
        print("="*60)
        
        pages_to_test = [
            ('home', 'Home Page'),
            ('about', 'About Page'),
            ('destinations', 'Destinations Page'),
        ]
        
        for url_name, description in pages_to_test:
            try:
                response = self.client.get(reverse(url_name))
                content = response.content.decode('utf-8')
                
                # Check for SEO elements
                seo_elements = [
                    ('meta name="description"', 'Meta description'),
                    ('meta name="keywords"', 'Meta keywords'),
                    ('meta property="og:title"', 'Open Graph title'),
                    ('meta property="og:description"', 'Open Graph description'),
                    ('title>', 'Page title'),
                ]
                
                for element, element_name in seo_elements:
                    if element in content:
                        self.log_result(f"{description} - {element_name}", "PASS", "SEO element found")
                    else:
                        self.log_result(f"{description} - {element_name}", "FAIL", "SEO element missing")
                        
            except Exception as e:
                self.log_result(f"{description} - SEO", "ERROR", f"Exception: {str(e)}")
    
    def test_database_content(self):
        """Test database content and models"""
        print("\n" + "="*60)
        print("TESTING DATABASE CONTENT")
        print("="*60)
        
        # Test Article model
        try:
            article_count = Article.objects.count()
            self.log_result("Database - Articles", "PASS", f"Found {article_count} articles")
            
            if article_count > 0:
                # Test article with AI content
                ai_articles = Article.objects.filter(
                    structured_content__isnull=False
                ).exclude(structured_content={})
                
                self.log_result("Database - AI Content", "PASS", f"Found {ai_articles.count()} articles with AI content")
                
                # Test article without AI content
                no_ai_articles = Article.objects.filter(
                    structured_content__isnull=True
                ) | Article.objects.filter(structured_content={})
                
                self.log_result("Database - No AI Content", "PASS", f"Found {no_ai_articles.count()} articles without AI content")
            else:
                self.log_result("Database - Content", "WARN", "No articles found in database")
                
        except Exception as e:
            self.log_result("Database Content", "ERROR", f"Exception: {str(e)}")
    
    def test_url_patterns(self):
        """Test URL patterns are correctly configured"""
        print("\n" + "="*60)
        print("TESTING URL PATTERNS")
        print("="*60)
        
        try:
            from articles.urls import urlpatterns
            
            expected_urls = [
                'home',
                'article_list', 
                'article_detail',
                'destinations',
                'about',
                'points_guide',
                'travel_tips',
                'contact',
                'privacy_policy',
                'terms_of_service',
                'cookie_policy',
            ]
            
            url_names = [pattern.name for pattern in urlpatterns if hasattr(pattern, 'name') and pattern.name]
            
            for expected_url in expected_urls:
                if expected_url in url_names:
                    self.log_result(f"URL Pattern: {expected_url}", "PASS", "URL pattern found")
                else:
                    self.log_result(f"URL Pattern: {expected_url}", "FAIL", "URL pattern missing")
                    
        except Exception as e:
            self.log_result("URL Patterns", "ERROR", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("🚀 Starting TravelPoints Website Verification")
        print("="*60)
        
        self.test_url_patterns()
        self.test_database_content()
        self.test_all_pages()
        self.test_article_detail_pages()
        self.test_navigation_links()
        self.test_footer_links()
        self.test_seo_elements()
        
        # Summary
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.results if r['status'] == 'ERROR'])
        skipped_tests = len([r for r in self.results if r['status'] == 'SKIP'])
        warn_tests = len([r for r in self.results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"⚠️  Warnings: {warn_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {result['test']}: {result['message']}")
        
        if success_rate >= 90:
            print("\n🎉 Website verification completed successfully!")
        else:
            print("\n⚠️  Some issues were found. Please review the failed tests above.")
        
        return self.results

if __name__ == "__main__":
    verifier = WebsiteVerification()
    results = verifier.run_all_tests() 