import os
import io
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from users.models import CustomUser
from properties.models import Amenity, Property, PropertyImage, Booking, Application, Review
from core.models import BlogPost

class Command(BaseCommand):
    help = 'Pre-populates the database with rich real estate mock data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing mock data load...")

        # 1. Create Users
        self.stdout.write("Creating users...")
        
        # Superuser Admin
        if not CustomUser.objects.filter(username='admin').exists():
            admin_user = CustomUser.objects.create_superuser(
                username='admin',
                email='admin@nyumbalink.com',
                password='AdminPassword123',
                role='admin',
                first_name='System',
                last_name='Administrator',
                is_verified=True
            )
            self.stdout.write("Admin user created: admin / AdminPassword123")
        else:
            admin_user = CustomUser.objects.get(username='admin')

        # Landlord
        if not CustomUser.objects.filter(username='japhet_landlord').exists():
            landlord = CustomUser.objects.create_user(
                username='japhet_landlord',
                email='japhetcheremo@gmail.com',
                password='LandlordPassword123',
                role='landlord',
                phone='+254 719 678 760',
                first_name='Japhet',
                last_name='Cheremo',
                is_verified=True,
                bio='Professional landlord offering high-end premium housing experiences in Nairobi, Mombasa, and Kisumu.'
            )
            self.stdout.write("Landlord created: japhet_landlord / LandlordPassword123")
        else:
            landlord = CustomUser.objects.get(username='japhet_landlord')

        # Tenant
        if not CustomUser.objects.filter(username='tenant_john').exists():
            tenant = CustomUser.objects.create_user(
                username='tenant_john',
                email='john@gmail.com',
                password='TenantPassword123',
                role='tenant',
                phone='+254 712 345 678',
                first_name='John',
                last_name='Doe',
                bio='Moving to Nairobi Westlands for work. Looking for a neat 1 or 2 bedroom apartment.'
            )
            self.stdout.write("Tenant created: tenant_john / TenantPassword123")
        else:
            tenant = CustomUser.objects.get(username='tenant_john')

        # 2. Create Amenities
        self.stdout.write("Creating amenities...")
        amenities_data = [
            ("Parking", "fa-solid fa-square-parking"),
            ("Water Availability", "fa-solid fa-faucet-drip"),
            ("Electricity", "fa-solid fa-bolt"),
            ("WiFi", "fa-solid fa-wifi"),
            ("Swimming Pool", "fa-solid fa-person-swimming"),
            ("Gym", "fa-solid fa-dumbbell"),
            ("CCTV", "fa-solid fa-video"),
            ("Security Guard", "fa-solid fa-user-shield"),
            ("Lift", "fa-solid fa-elevator"),
            ("Balcony", "fa-solid fa-door-open"),
            ("Garden", "fa-solid fa-tree"),
            ("Borehole", "fa-solid fa-bore-hole"),
            ("Backup Generator", "fa-solid fa-charging-station"),
            ("Wardrobes", "fa-solid fa-boxes-packing"),
            ("Kitchen Cabinets", "fa-solid fa-kitchen-set"),
            ("Hot Shower", "fa-solid fa-shower"),
            ("Pet Friendly", "fa-solid fa-paw"),
            ("Garbage Collection", "fa-solid fa-trash-can")
        ]
        
        amenity_instances = {}
        for name, icon in amenities_data:
            amenity, created = Amenity.objects.get_or_create(name=name, defaults={'icon': icon})
            amenity_instances[name] = amenity

        # 3. Create Properties
        self.stdout.write("Creating properties and downloading images...")
        properties_data = [
            {
                'title': 'Sleek 2 Bedroom Executive Apartment',
                'description': 'A premium executive 2-bedroom rental apartment located in the secure heart of Westlands. Features high ceilings, dynamic open plan kitchen, and uninterrupted borehole water supply.',
                'category': 'two_bedroom',
                'monthly_rent': 45000.00,
                'deposit': 45000.00,
                'service_charge': 2500.00,
                'bedrooms': 2,
                'bathrooms': 2,
                'square_footage': 950,
                'floor_number': 3,
                'county': 'Nairobi',
                'town': 'Westlands',
                'estate': 'Raphta Road',
                'address': 'Westlands Heights, Block B, Flat 3B',
                'latitude': -1.2612,
                'longitude': 36.8021,
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'house_rules': 'No loud music after 10 PM.\nPets allowed upon notification.',
                'nearby_schools': 'Westlands Primary, St. Marys School',
                'nearby_hospitals': 'Aga Khan Hospital, MP Shah Hospital',
                'nearby_shopping': 'Sarit Centre, Westgate Mall',
                'nearby_bus_stops': 'Sarit Centre Stage',
                'status': 'available',
                'amenities': ['Parking', 'Water Availability', 'Electricity', 'WiFi', 'CCTV', 'Security Guard', 'Hot Shower', 'Kitchen Cabinets', 'Garbage Collection'],
                'image_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800'
            },
            {
                'title': 'Luxurious Coastal Villa with Ocean View',
                'description': 'Stunning modern 4-bedroom villa in Nyali Mombasa. Complete with a private swimming pool, landscaped gardens, direct beach access, and state of the art CCTV installations.',
                'category': 'villa',
                'monthly_rent': 120000.00,
                'deposit': 120000.00,
                'service_charge': 5000.00,
                'bedrooms': 4,
                'bathrooms': 4,
                'square_footage': 3200,
                'floor_number': 1,
                'county': 'Mombasa',
                'town': 'Nyali',
                'estate': 'Links Road',
                'address': 'Ocean Crest Court, Villa 4',
                'latitude': -4.0298,
                'longitude': 39.7121,
                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'house_rules': 'Quiet hours: 11 PM - 7 AM.\nPets allowed.',
                'nearby_schools': 'Mombasa Academy, Light Academy',
                'nearby_hospitals': 'The Mombasa Hospital Nyali Branch',
                'nearby_shopping': 'City Mall Nyali, Naivas Centre',
                'nearby_bus_stops': 'Nyali Bridge Stage',
                'status': 'available',
                'amenities': ['Parking', 'Water Availability', 'Electricity', 'CCTV', 'Security Guard', 'Swimming Pool', 'Gym', 'Garden', 'Backup Generator', 'Pet Friendly'],
                'image_url': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'
            },
            {
                'title': 'Cozy Glassmorphic Studio Apartment',
                'description': 'A fully furnished minimalist studio apartment in Kilimani. Perfect for young professionals. High-speed fibre internet included, featuring modern glass dividers.',
                'category': 'studio',
                'monthly_rent': 22000.00,
                'deposit': 22000.00,
                'service_charge': 1500.00,
                'bedrooms': 0,
                'bathrooms': 1,
                'square_footage': 420,
                'floor_number': 5,
                'county': 'Nairobi',
                'town': 'Kilimani',
                'estate': 'Lenana Road',
                'address': 'Lenana View Apartments, Room 502',
                'latitude': -1.2912,
                'longitude': 36.7925,
                'video_url': '',
                'house_rules': 'No subletting.\nQuiet tenancy preferred.',
                'nearby_schools': 'Cavina School, French School',
                'nearby_hospitals': 'Coptic Hospital, Nairobi Hospital',
                'nearby_shopping': 'Yaya Centre, Prestige Plaza',
                'nearby_bus_stops': 'Yaya Stage',
                'status': 'available',
                'amenities': ['Water Availability', 'Electricity', 'WiFi', 'CCTV', 'Lift', 'Balcony', 'Kitchen Cabinets', 'Hot Shower', 'Garbage Collection'],
                'image_url': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'
            },
            {
                'title': 'Elegant 3 Bedroom Family Home',
                'description': 'Family-oriented 3-bedroom house in the peaceful leafy suburb of Milimani, Kisumu. Features a spacious private garden, secure fencing, and a separate laundry area.',
                'category': 'three_bedroom',
                'monthly_rent': 35000.00,
                'deposit': 35000.00,
                'service_charge': 0.00,
                'bedrooms': 3,
                'bathrooms': 2,
                'square_footage': 1500,
                'floor_number': 1,
                'county': 'Kisumu',
                'town': 'Kisumu',
                'estate': 'Milimani',
                'address': 'Lake Breeze Court, House 12',
                'latitude': -0.1082,
                'longitude': 34.7562,
                'video_url': '',
                'house_rules': 'Take care of the garden lawn.\nPet friendly.',
                'nearby_schools': 'Kisumu International School',
                'nearby_hospitals': 'Aga Khan Kisumu Hospital',
                'nearby_shopping': 'West End Mall, United Mall',
                'nearby_bus_stops': 'Milimani Stage',
                'status': 'available',
                'amenities': ['Parking', 'Water Availability', 'Electricity', 'Security Guard', 'Balcony', 'Garden', 'Hot Shower', 'Pet Friendly'],
                'image_url': 'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=800'
            }
        ]

        for p_data in properties_data:
            # Check if property already exists
            if Property.objects.filter(title=p_data['title']).exists():
                self.stdout.write(f"Property already exists: {p_data['title']}")
                continue
                
            prop = Property.objects.create(
                title=p_data['title'],
                description=p_data['description'],
                category=p_data['category'],
                monthly_rent=p_data['monthly_rent'],
                deposit=p_data['deposit'],
                service_charge=p_data['service_charge'],
                bedrooms=p_data['bedrooms'],
                bathrooms=p_data['bathrooms'],
                square_footage=p_data['square_footage'],
                floor_number=p_data['floor_number'],
                county=p_data['county'],
                town=p_data['town'],
                estate=p_data['estate'],
                address=p_data['address'],
                latitude=p_data['latitude'],
                longitude=p_data['longitude'],
                video_url=p_data['video_url'],
                house_rules=p_data['house_rules'],
                nearby_schools=p_data['nearby_schools'],
                nearby_hospitals=p_data['nearby_hospitals'],
                nearby_shopping=p_data['nearby_shopping'],
                nearby_bus_stops=p_data['nearby_bus_stops'],
                status=p_data['status'],
                created_by=landlord
            )
            
            # Map amenities
            for am_name in p_data['amenities']:
                if am_name in amenity_instances:
                    prop.amenities.add(amenity_instances[am_name])

            # Download Image
            try:
                r = requests.get(p_data['image_url'], timeout=10)
                if r.status_code == 200:
                    prop_image = PropertyImage(property=prop, is_featured=True)
                    img_name = f"property_{prop.id}.jpg"
                    prop_image.image.save(img_name, ContentFile(r.content), save=True)
                    self.stdout.write(f"Created property '{prop.title}' with image.")
                else:
                    self.stdout.write(f"Failed to download image for '{prop.title}'. Status: {r.status_code}")
            except Exception as e:
                self.stdout.write(f"Error downloading image for '{prop.title}': {str(e)}")

        # 4. Create Blog Posts
        self.stdout.write("Creating blog posts...")
        blogs_data = [
            {
                'title': '5 Critical Things to Inspect Before Renting a House in Nairobi',
                'content': 'Moving to a new rental apartment in Nairobi can be exciting but full of hidden traps. Always check these five elements:\n\n1. Water consistency: Ask neighbors if borehole water runs daily or if water rationing is active.\n2. Token meter readings: Verify the electric token meter is not carrying debt from past tenants.\n3. Security guards: Walk by at night to check security staffing levels.\n4. Mobile network signal: Thick concrete walls in some estates block signals.\n5. Distance to transport links: Avoid long rough roads if you rely on public transport.',
                'category': 'rental_tips'
            },
            {
                'title': 'Smart Space-Saving Hacks for Studio Apartments & Bedsitters',
                'content': 'Studio apartments (commonly bedsitters) are pocket-friendly but require smart organizing. Use folding multi-purpose desks, floating shelves to keep floor spaces clear, and vertical storage boxes. Introduce partition divider screens or decorative bookshelves to separate your bed zone from the living and kitchen spaces, giving the room a multi-room aesthetic layout.',
                'category': 'interior_design'
            },
            {
                'title': 'Understanding Service Charges & Security Deposit Refund Policies',
                'content': 'Service charges cover communal tasks like garbage collection, security guard wages, elevator maintenance, and cleaning. Always ask what your monthly charge covers. Additionally, document the initial state of the walls, plumbing, and fixtures with photos upon move-in to protect your deposit refund when moving out.',
                'category': 'moving_guides'
            }
        ]

        for b_data in blogs_data:
            if not BlogPost.objects.filter(title=b_data['title']).exists():
                BlogPost.objects.create(
                    title=b_data['title'],
                    content=b_data['content'],
                    category=b_data['category'],
                    author=admin_user
                )
                self.stdout.write(f"Blog post created: {b_data['title']}")

        # 5. Create Reviews
        self.stdout.write("Creating reviews...")
        first_prop = Property.objects.first()
        if first_prop and not Review.objects.filter(property=first_prop).exists():
            Review.objects.create(
                tenant=tenant,
                property=first_prop,
                rating=5,
                text="Absolutely gorgeous apartment! The water is constant, the security guard is extremely polite, and the location close to Sarit Centre is highly convenient."
            )
            Review.objects.create(
                tenant=tenant,
                property=first_prop,
                rating=4,
                text="Great house and very clean rooms. The landlord, Japhet, is highly responsive to maintenance calls."
            )
            self.stdout.write("Reviews created for first property.")

        # 6. Create Booking & Application
        self.stdout.write("Creating bookings and applications...")
        if first_prop:
            if not Booking.objects.filter(tenant=tenant, property=first_prop).exists():
                Booking.objects.create(
                    tenant=tenant,
                    property=first_prop,
                    date="2026-07-02",
                    time="14:00:00",
                    message="Hi Japhet, I would like to schedule a physical viewing inspect this room on Thursday afternoon.",
                    status="pending"
                )
            if not Application.objects.filter(tenant=tenant, property=first_prop).exists():
                Application.objects.create(
                    tenant=tenant,
                    property=first_prop,
                    message="I work in Westlands and am ready to pay deposit and move in by July 15th.",
                    status="pending"
                )
            self.stdout.write("Booking and Application created.")

        self.stdout.write(self.style.SUCCESS("Mock data load completed successfully!"))
