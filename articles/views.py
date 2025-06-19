from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Article
from django.db.models import Q
from .services import rewrite_article_content
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    """Home page with featured articles and overview"""
    # Get featured articles (latest 6 with AI content)
    featured_articles = Article.objects.filter(
        structured_content__isnull=False
    ).exclude(
        structured_content={}
    ).order_by('-date_published')[:6]
    
    # Get latest articles for the grid
    latest_articles = Article.objects.all().order_by('-date_published')[:12]
    
    # Get articles by category for different sections
    points_articles = Article.objects.filter(
        categories__icontains='points'
    ).order_by('-date_published')[:4]
    
    travel_articles = Article.objects.filter(
        categories__icontains='travel'
    ).order_by('-date_published')[:4]
    
    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'points_articles': points_articles,
        'travel_articles': travel_articles,
    }
    return render(request, 'articles/home.html', context)

def article_list(request):
    articles = Article.objects.all().order_by('-date_published')
    print(f"Number of articles found: {articles.count()}")  # Debug print
    
    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add some test data if no articles exist
    if not articles.exists():
        print("No articles found in database")
        test_articles = [
            {
                'title': 'Test Article 1',
                'author': 'Test Author',
                'date_published': '2024-03-13',
                'content': 'This is a test article content.',
                'url': '#',
                'source': 'Test Source'
            },
            {
                'title': 'Test Article 2',
                'author': 'Test Author',
                'date_published': '2024-03-13',
                'content': 'This is another test article content.',
                'url': '#',
                'source': 'Test Source'
            }
        ]
        context = {'articles': test_articles}
    else:
        context = {
            'articles': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
    
    return render(request, 'articles/article_list.html', context)

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Check if we need to generate AI content
    if not article.structured_content and article.content:
        logger.info(f"Generating AI content for article {article_id}: {article.title}")
        
        try:
            # Generate structured content using AI
            structured_content = rewrite_article_content(article.content)
            
            if structured_content:
                # Save the AI-generated content to the database
                article.structured_content = structured_content
                article.save()
                logger.info(f"Successfully saved AI content for article {article_id}")
            else:
                logger.warning(f"Failed to generate AI content for article {article_id}")
                
        except Exception as e:
            logger.error(f"Error generating AI content for article {article_id}: {str(e)}")
    
    # Prepare context with fallback for paragraphs if no structured content
    context = {'article': article}
    
    # If no structured_content, provide paragraphs for fallback
    if not article.structured_content and article.content:
        # Split content into paragraphs for basic display
        paragraphs = [p.strip() for p in article.content.split('\n') if p.strip()]
        context['paragraphs'] = paragraphs
    
    return render(request, 'articles/article_detail.html', context)

def destinations(request):
    """Destinations page showcasing travel destinations"""
    # Get articles related to destinations
    destination_articles = Article.objects.filter(
        Q(categories__icontains='destination') |
        Q(categories__icontains='travel') |
        Q(title__icontains='destination')
    ).order_by('-date_published')[:12]
    
    # Popular destinations data
    popular_destinations = [
        {
            'name': 'Bali, Indonesia',
            'description': 'Tropical paradise with stunning beaches and rich culture',
            'image': 'https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=800',
            'category': 'Beach & Culture',
            'slug': 'bali-indonesia'
        },
        {
            'name': 'Tokyo, Japan',
            'description': 'Modern metropolis blending tradition with innovation',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
            'category': 'City & Culture',
            'slug': 'tokyo-japan'
        },
        {
            'name': 'Paris, France',
            'description': 'City of love, art, and culinary excellence',
            'image': 'https://images.unsplash.com/photo-1502602898534-47d3c0c0b8b8?w=800',
            'category': 'Culture & Romance',
            'slug': 'paris-france'
        },
        {
            'name': 'New York City, USA',
            'description': 'The city that never sleeps with endless possibilities',
            'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800',
            'category': 'City & Entertainment',
            'slug': 'new-york-city-usa'
        },
        {
            'name': 'Santorini, Greece',
            'description': 'Stunning sunsets and white-washed architecture',
            'image': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800',
            'category': 'Island & Romance',
            'slug': 'santorini-greece'
        },
        {
            'name': 'Machu Picchu, Peru',
            'description': 'Ancient Incan citadel in the Andes mountains',
            'image': 'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800',
            'category': 'Adventure & History',
            'slug': 'machu-picchu-peru'
        }
    ]
    
    context = {
        'destination_articles': destination_articles,
        'popular_destinations': popular_destinations,
    }
    return render(request, 'articles/destinations.html', context)

def about(request):
    """About page with company information"""
    context = {
        'mission_statement': {
            'title': 'Our Mission',
            'description': 'To democratize luxury travel by making points and miles accessible to everyone. We believe that extraordinary travel experiences shouldn\'t be limited to the wealthy - they should be achievable through smart strategies and informed decisions.',
            'icon': 'fas fa-compass'
        },
        'core_values': [
            {
                'title': 'Accessibility',
                'description': 'Making complex travel strategies simple and understandable for everyone',
                'icon': 'fas fa-universal-access'
            },
            {
                'title': 'Innovation',
                'description': 'Leveraging AI and technology to provide cutting-edge travel insights',
                'icon': 'fas fa-lightbulb'
            },
            {
                'title': 'Community',
                'description': 'Building a supportive network of travelers who share knowledge and experiences',
                'icon': 'fas fa-users'
            },
            {
                'title': 'Transparency',
                'description': 'Providing honest, unbiased advice without hidden agendas or sponsored content',
                'icon': 'fas fa-eye'
            }
        ],
        'stats': {
            'articles_published': Article.objects.count(),
            'destinations_covered': 150,
            'readers_helped': '50K+',
            'years_experience': 8
        }
    }
    return render(request, 'articles/about.html', context)

def points_guide(request):
    """Points and miles guide page"""
    # Get articles related to points and miles
    points_articles = Article.objects.filter(
        Q(categories__icontains='points') |
        Q(categories__icontains='miles') |
        Q(title__icontains='points') |
        Q(title__icontains='miles')
    ).order_by('-date_published')[:10]
    
    context = {
        'points_articles': points_articles,
        'guides': [
            {
                'title': 'Credit Card Points Basics',
                'description': 'Learn the fundamentals of earning and redeeming credit card points',
                'icon': 'fas fa-credit-card',
                'difficulty': 'Beginner'
            },
            {
                'title': 'Airline Miles Strategies',
                'description': 'Master the art of earning and using airline miles effectively',
                'icon': 'fas fa-plane',
                'difficulty': 'Intermediate'
            },
            {
                'title': 'Hotel Loyalty Programs',
                'description': 'Maximize your hotel stays with loyalty program benefits',
                'icon': 'fas fa-hotel',
                'difficulty': 'Intermediate'
            },
            {
                'title': 'Advanced Redemption Techniques',
                'description': 'Learn advanced strategies for maximum point value',
                'icon': 'fas fa-chart-line',
                'difficulty': 'Advanced'
            }
        ]
    }
    return render(request, 'articles/points_guide.html', context)

def travel_tips(request):
    """Travel tips and advice page"""
    # Get travel tips articles
    tips_articles = Article.objects.filter(
        Q(categories__icontains='tips') |
        Q(categories__icontains='advice') |
        Q(title__icontains='tips') |
        Q(title__icontains='advice')
    ).order_by('-date_published')[:12]
    
    context = {
        'tips_articles': tips_articles,
        'travel_tips': [
            {
                'category': 'Packing',
                'tips': [
                    'Roll clothes instead of folding to save space',
                    'Use packing cubes for organization',
                    'Pack versatile clothing items',
                    'Don\'t forget essential documents'
                ]
            },
            {
                'category': 'Booking',
                'tips': [
                    'Book flights on Tuesdays for best deals',
                    'Use incognito mode when searching',
                    'Consider alternative airports',
                    'Set up price alerts'
                ]
            },
            {
                'category': 'Safety',
                'tips': [
                    'Keep copies of important documents',
                    'Use hotel safes for valuables',
                    'Research local customs and laws',
                    'Stay aware of your surroundings'
                ]
            },
            {
                'category': 'Budget',
                'tips': [
                    'Set a daily spending limit',
                    'Use local transportation',
                    'Eat where locals eat',
                    'Book activities in advance'
                ]
            }
        ]
    }
    return render(request, 'articles/travel_tips.html', context)

def contact(request):
    """Contact page with contact form and information"""
    context = {
        'contact_info': {
            'email': 'hello@travelpoints.com',
            'phone': '+1 (555) 123-4567',
            'address': '123 Travel Street, Adventure City, AC 12345',
            'hours': 'Monday - Friday: 9:00 AM - 6:00 PM EST'
        }
    }
    return render(request, 'articles/contact.html', context)

def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'articles/privacy_policy.html')

def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'articles/terms_of_service.html')

def cookie_policy(request):
    """Cookie policy page"""
    return render(request, 'articles/cookie_policy.html')

def destination_detail(request, destination_slug):
    """Individual destination detail page"""
    # Destination data - in a real app, this would come from a database
    destinations_data = {
        'bali-indonesia': {
            'name': 'Bali, Indonesia',
            'description': 'Tropical paradise with stunning beaches and rich culture',
            'long_description': 'Bali, the famed Island of the Gods, is a paradise for travelers seeking a perfect blend of natural beauty, cultural richness, and spiritual tranquility. This Indonesian gem offers everything from pristine beaches and lush rice terraces to ancient temples and vibrant nightlife.',
            'image': 'https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=800',
            'category': 'Beach & Culture',
            'highlights': [
                'Sacred Monkey Forest in Ubud',
                'Tegallalang Rice Terraces',
                'Tanah Lot Temple',
                'Seminyak Beach',
                'Mount Batur Sunrise Trek'
            ],
            'best_time': 'April to October (Dry Season)',
            'currency': 'Indonesian Rupiah (IDR)',
            'language': 'Indonesian, Balinese',
            'tips': [
                'Respect local customs and dress modestly when visiting temples',
                'Learn a few basic Indonesian phrases',
                'Try local cuisine like Nasi Goreng and Satay',
                'Book accommodations in advance during peak season',
                'Use local transportation or hire a driver for convenience'
            ],
            'points_opportunities': [
                'Use Chase Sapphire Reserve for 3x points on dining',
                'Transfer points to Singapore Airlines for flights',
                'Book luxury hotels through Amex Fine Hotels & Resorts',
                'Use Citi Prestige for 4th night free at hotels'
            ]
        },
        'tokyo-japan': {
            'name': 'Tokyo, Japan',
            'description': 'Modern metropolis blending tradition with innovation',
            'long_description': 'Tokyo is a fascinating blend of ultramodern and traditional, offering visitors an exciting mix of cutting-edge technology, ancient temples, and world-class cuisine. This dynamic city never sleeps and provides endless opportunities for exploration.',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800',
            'category': 'City & Culture',
            'highlights': [
                'Senso-ji Temple in Asakusa',
                'Shibuya Crossing',
                'Tokyo Skytree',
                'Tsukiji Outer Market',
                'Meiji Shrine'
            ],
            'best_time': 'March to May (Cherry Blossom) and September to November',
            'currency': 'Japanese Yen (JPY)',
            'language': 'Japanese',
            'tips': [
                'Get a Japan Rail Pass for efficient travel',
                'Learn basic Japanese etiquette',
                'Try authentic ramen and sushi',
                'Use IC cards for convenient transportation',
                'Respect quiet zones on public transport'
            ],
            'points_opportunities': [
                'Use Amex Platinum for 5x points on flights',
                'Transfer points to ANA for award flights',
                'Book luxury hotels through Marriott Bonvoy',
                'Use Chase Sapphire Preferred for dining rewards'
            ]
        },
        'paris-france': {
            'name': 'Paris, France',
            'description': 'City of love, art, and culinary excellence',
            'long_description': 'Paris, the City of Light, is a timeless destination that captivates visitors with its iconic landmarks, world-class museums, and unparalleled culinary scene. From the Eiffel Tower to charming neighborhoods, Paris offers an unforgettable experience.',
            'image': 'https://images.unsplash.com/photo-1502602898534-47d3c0c0b8b8?w=800',
            'category': 'Culture & Romance',
            'highlights': [
                'Eiffel Tower',
                'Louvre Museum',
                'Notre-Dame Cathedral',
                'Champs-Élysées',
                'Montmartre and Sacré-Cœur'
            ],
            'best_time': 'April to June and September to October',
            'currency': 'Euro (EUR)',
            'language': 'French',
            'tips': [
                'Learn basic French phrases',
                'Get a Paris Museum Pass for savings',
                'Try local pastries and wine',
                'Use the efficient metro system',
                'Book restaurant reservations in advance'
            ],
            'points_opportunities': [
                'Use Chase Sapphire Reserve for 3x on dining',
                'Transfer points to Air France/KLM for flights',
                'Book luxury hotels through Hyatt',
                'Use Amex Gold for 4x on dining'
            ]
        },
        'new-york-city-usa': {
            'name': 'New York City, USA',
            'description': 'The city that never sleeps with endless possibilities',
            'long_description': 'New York City is the ultimate urban playground, offering world-class entertainment, diverse cuisine, iconic landmarks, and endless cultural experiences. From Times Square to Central Park, NYC has something for everyone.',
            'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800',
            'category': 'City & Entertainment',
            'highlights': [
                'Times Square',
                'Central Park',
                'Statue of Liberty',
                'Broadway Shows',
                'Empire State Building'
            ],
            'best_time': 'April to June and September to November',
            'currency': 'US Dollar (USD)',
            'language': 'English',
            'tips': [
                'Get a MetroCard for subway access',
                'Book Broadway tickets in advance',
                'Try diverse cuisines in different neighborhoods',
                'Visit museums on free days',
                'Walk across Brooklyn Bridge for great views'
            ],
            'points_opportunities': [
                'Use Amex Platinum for 5x on flights',
                'Transfer points to Delta for domestic flights',
                'Book luxury hotels through Marriott or Hilton',
                'Use Chase Sapphire Reserve for dining and travel'
            ]
        },
        'santorini-greece': {
            'name': 'Santorini, Greece',
            'description': 'Stunning sunsets and white-washed architecture',
            'long_description': 'Santorini is a dream destination known for its dramatic caldera views, stunning sunsets, and iconic white-washed buildings. This Greek island offers a perfect blend of natural beauty, history, and luxury.',
            'image': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800',
            'category': 'Island & Romance',
            'highlights': [
                'Oia Sunset Views',
                'Fira Town',
                'Red Beach',
                'Ancient Thera',
                'Wine Tasting Tours'
            ],
            'best_time': 'May to October (Peak: June to September)',
            'currency': 'Euro (EUR)',
            'language': 'Greek',
            'tips': [
                'Book accommodations with caldera views',
                'Rent a car to explore the island',
                'Try local wines and Mediterranean cuisine',
                'Visit during shoulder season for better prices',
                'Book sunset dinner reservations early'
            ],
            'points_opportunities': [
                'Use Chase Sapphire Reserve for 3x on dining',
                'Transfer points to Aegean Airlines',
                'Book luxury hotels through Marriott',
                'Use Amex Fine Hotels & Resorts for elite benefits'
            ]
        },
        'machu-picchu-peru': {
            'name': 'Machu Picchu, Peru',
            'description': 'Ancient Incan citadel in the Andes mountains',
            'long_description': 'Machu Picchu, the lost city of the Incas, is one of the most impressive archaeological sites in the world. This UNESCO World Heritage site offers breathtaking mountain views and a fascinating glimpse into ancient civilization.',
            'image': 'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800',
            'category': 'Adventure & History',
            'highlights': [
                'Machu Picchu Citadel',
                'Inca Trail Trek',
                'Huayna Picchu Mountain',
                'Sacred Valley',
                'Cusco Historic Center'
            ],
            'best_time': 'April to October (Dry Season)',
            'currency': 'Peruvian Sol (PEN)',
            'language': 'Spanish',
            'tips': [
                'Acclimatize to altitude in Cusco first',
                'Book Machu Picchu tickets months in advance',
                'Hire a guide for better understanding',
                'Try local cuisine like ceviche and quinoa',
                'Pack for varying weather conditions'
            ],
            'points_opportunities': [
                'Use Amex Platinum for 5x on flights',
                'Transfer points to LATAM Airlines',
                'Book luxury hotels through Marriott',
                'Use Chase Sapphire Reserve for travel insurance'
            ]
        }
    }
    
    destination = destinations_data.get(destination_slug)
    if not destination:
        from django.http import Http404
        raise Http404("Destination not found")
    
    # Get related articles for this destination
    related_articles = Article.objects.filter(
        Q(title__icontains=destination['name'].split(',')[0]) |
        Q(content__icontains=destination['name'].split(',')[0])
    ).order_by('-date_published')[:6]
    
    context = {
        'destination': destination,
        'related_articles': related_articles,
    }
    return render(request, 'articles/destination_detail.html', context)
