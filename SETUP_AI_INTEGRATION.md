# AI Integration Setup Guide

## Overview
This guide will help you set up the OpenAI AI integration for your travel articles website. The system will automatically rewrite and structure your scraped articles using AI.

## Prerequisites
1. Python 3.8+ installed
2. Django project set up
3. Articles already scraped and in the database

## Step 1: Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Copy the API key (it starts with `sk-`)

## Step 2: Configure API Key
1. Open the `.env` file in your project root
2. Replace `your_openai_api_key_here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
3. Save the file

## Step 3: Test the Integration
Run the test script to verify everything works:
```bash
python test_openai.py
```

If successful, you should see:
```
✅ OpenAI integration successful!
✅ Test passed! You can now run the management command.
```

## Step 4: Generate AI Content
Once the test passes, you can generate AI content for your articles:

### Generate for all articles:
```bash
python manage.py generate_ai_content
```

### Generate for limited articles (recommended for first run):
```bash
python manage.py generate_ai_content --limit 5
```

### Dry run (see what would be processed):
```bash
python manage.py generate_ai_content --dry-run
```

## Step 5: View Results
1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```
2. Visit any article page (e.g., `http://127.0.0.1:8000/articles/1/`)
3. You should now see AI-generated content with:
   - Summary section
   - Key takeaways
   - Structured sections with headings and paragraphs

## How It Works

### Database Fields
- `content`: Original scraped content
- `structured_content`: AI-generated structured content (JSON)
- `rewritten_content`: Legacy field (not used in current version)

### AI Processing
1. When you visit an article page, if `structured_content` is empty, the system automatically calls OpenAI
2. The AI rewrites the content into a structured format with:
   - Summary
   - Key points
   - Sections (headings, paragraphs, quotes)
3. The result is saved to the database for future use

### Template Display
- If `structured_content` exists: Shows AI-generated content with proper formatting
- If not: Falls back to original content split into paragraphs

## Troubleshooting

### "OpenAI API key not found"
- Make sure you've set the API key in the `.env` file
- Restart your Django server after changing the `.env` file
- Check that the API key starts with `sk-`

### "Rate limit exceeded"
- The system includes delays between requests
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan if you have many articles

### "No content available"
- Check that your articles have content in the `content` field
- Run the scraper again if needed

### "AI content generated but no sections found"
- This is a fallback message if the AI response doesn't match expected format
- The system will still show the original content

## Cost Considerations
- OpenAI charges per token used
- Each article typically costs $0.01-$0.05 depending on length
- Monitor your usage at [OpenAI Usage](https://platform.openai.com/usage)

## Advanced Configuration

### Customize AI Prompt
Edit `articles/services.py` to modify the AI prompt for different content styles.

### Batch Processing
For large datasets, consider running the management command in batches:
```bash
python manage.py generate_ai_content --limit 10
# Wait for completion, then:
python manage.py generate_ai_content --limit 10
```

### Error Handling
The system includes comprehensive error handling and logging. Check Django logs for detailed error messages.

## Support
If you encounter issues:
1. Check the Django logs for error messages
2. Verify your API key is correct
3. Test with a single article first
4. Ensure you have sufficient OpenAI credits 