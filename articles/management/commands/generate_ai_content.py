from django.core.management.base import BaseCommand
from articles.models import Article
from articles.services import rewrite_article_content
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate AI content for articles that don\'t have structured_content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of articles to process'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without actually doing it'
        )

    def handle(self, *args, **options):
        # Get articles that need AI content generation
        articles = Article.objects.filter(
            structured_content__isnull=True
        ).exclude(
            content__isnull=True
        ).exclude(
            content=''
        )
        
        if options['limit']:
            articles = articles[:options['limit']]
        
        total_articles = articles.count()
        
        if total_articles == 0:
            self.stdout.write(
                self.style.SUCCESS('No articles found that need AI content generation.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {total_articles} articles to process.')
        )
        
        if options['dry_run']:
            self.stdout.write('DRY RUN - No changes will be made.')
            for article in articles:
                self.stdout.write(f'Would process: {article.title} (ID: {article.id})')
            return
        
        processed = 0
        failed = 0
        
        for article in articles:
            try:
                self.stdout.write(f'Processing article {processed + 1}/{total_articles}: {article.title}')
                
                # Generate AI content
                structured_content = rewrite_article_content(article.content)
                
                if structured_content:
                    # Save to database
                    article.structured_content = structured_content
                    article.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Successfully processed: {article.title}')
                    )
                    processed += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Failed to generate content for: {article.title}')
                    )
                    failed += 1
                
                # Add delay to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {article.title}: {str(e)}')
                )
                failed += 1
                continue
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Processing complete!')
        )
        self.stdout.write(f'Total articles: {total_articles}')
        self.stdout.write(f'Successfully processed: {processed}')
        self.stdout.write(f'Failed: {failed}')
        self.stdout.write('='*50) 