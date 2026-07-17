import asyncio
import random
from datetime import datetime, timedelta
from app.core.database import async_session_factory, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.item import Item
from app.models.interaction import Interaction
from app.models.rating import Rating
from sqlalchemy import text


CATEGORIES = ["Movies", "Books", "Music", "Games", "Courses"]

MOVIE_TITLES = [
    "Inception", "The Dark Knight", "Interstellar", "The Matrix", "Pulp Fiction",
    "Forrest Gump", "The Shawshank Redemption", "Gladiator", "The Godfather", "Titanic",
    "Avengers: Endgame", "Parasite", "Joker", "Dune", "Everything Everywhere All at Once",
    "The Batman", "Oppenheimer", "Barbie", "Spider-Man: No Way Home", "No Country for Old Men",
    "The Grand Budapest Hotel", "Whiplash", "Arrival", "Blade Runner 2049", "Mad Max: Fury Road",
    "The Social Network", "Get Out", "Her", "Moonlight", "La La Land",
    "Memento", "The Departed", "Casino Royale", "District 9", "Ex Machina",
    "The Prestige", "Shutter Island", "Gone Girl", "The Wolf of Wall Street", "Django Unchained",
]

BOOK_TITLES = [
    "Dune", "Neuromancer", "The Hitchhiker's Guide to the Galaxy", "1984", "Brave New World",
    "Fahrenheit 451", "The Great Gatsby", "To Kill a Mockingbird", "Catch-22", "Slaughterhouse-Five",
    "The Lord of the Rings", "Harry Potter and the Sorcerer's Stone", "The Alchemist", "Sapiens",
    "Atomic Habits", "Thinking, Fast and Slow", "The Art of War", "Meditations",
    "The Design of Everyday Things", "Clean Code", "Deep Work", "The Pragmatic Programmer",
    "Zero to One", "The Lean Startup", "Creativity Inc", "The Psychology of Money",
]

MUSIC_TITLES = [
    "Bohemian Rhapsody", "Stairway to Heaven", "Hotel California", "Imagine", "Billie Jean",
    "Smells Like Teen Spirit", "Hey Jude", "Yesterday", "Like a Rolling Stone", "Purple Rain",
    "Blinding Lights", "Shape of You", "Old Town Road", "Bad Guy", "Levitating",
    "Watermelon Sugar", "Dynamite", "Stay", "Heat Waves", "As It Was",
    "Flowers", "Anti-Hero", "Unholy", "Calm Down", "Kill Bill",
]

GAME_TITLES = [
    "The Witcher 3: Wild Hunt", "Red Dead Redemption 2", "The Last of Us Part II", "God of War",
    "Elden Ring", "Baldur's Gate 3", "Cyberpunk 2077", "Hades", "Disco Elysium",
    "Hollow Knight", "Celeste", "Portal 2", "Half-Life 2", "Minecraft",
    "Grand Theft Auto V", "The Legend of Zelda: Breath of the Wild", "Dark Souls",
    "Sekiro: Shadows Die Twice", "Bloodborne", "Resident Evil 4",
]

COURSE_TITLES = [
    "Machine Learning Specialization", "Deep Learning Specialization", "CS50: Introduction to Computer Science",
    "Python for Data Science", "React - The Complete Guide", "Node.js Masterclass",
    "Kubernetes for Beginners", "AWS Solutions Architect", "Data Structures and Algorithms",
    "System Design Interview Prep", "Full Stack Web Development", "iOS Development with Swift",
    "Cloud Computing Fundamentals", "DevOps Masterclass", "Natural Language Processing",
]

GENRES_MAP = {
    "Movies": ["Action", "Sci-Fi", "Drama", "Thriller", "Comedy", "Horror", "Romance", "Animation", "Documentary", "Adventure"],
    "Books": ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Self-Help", "Business", "Philosophy", "Technology", "Biography"],
    "Music": ["Rock", "Pop", "Hip-Hop", "Jazz", "Classical", "Electronic", "R&B", "Country", "Alternative", "Indie"],
    "Games": ["RPG", "Action", "Adventure", "Strategy", "Puzzle", "Platformer", "Simulation", "FPS", "Horror", "Indie"],
    "Courses": ["Programming", "Data Science", "AI/ML", "Web Development", "DevOps", "Design", "Business", "Security", "Mobile", "Cloud"],
}


def get_all_titles():
    titles = []
    for title in MOVIE_TITLES:
        titles.append({"title": title, "category": "Movies"})
    for title in BOOK_TITLES:
        titles.append({"title": title, "category": "Books"})
    for title in MUSIC_TITLES:
        titles.append({"title": title, "category": "Music"})
    for title in GAME_TITLES:
        titles.append({"title": title, "category": "Games"})
    for title in COURSE_TITLES:
        titles.append({"title": title, "category": "Courses"})
    return titles


async def seed():
    await init_db()
    async with async_session_factory() as db:
        existing = await db.execute(text("SELECT COUNT(*) FROM users"))
        count = existing.scalar()
        if count > 0:
            print(f"Database already has {count} users. Skipping seed.")
            return

        print("Creating admin user...")
        admin = User(
            email="admin@recommendation.ai",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Admin",
            is_admin=True,
            is_active=True,
        )
        db.add(admin)

        print("Creating test users...")
        users = []
        test_users = [
            ("alice@example.com", "alice", "password123", "Alice Johnson"),
            ("bob@example.com", "bob", "password123", "Bob Smith"),
            ("charlie@example.com", "charlie", "password123", "Charlie Brown"),
            ("diana@example.com", "diana", "password123", "Diana Prince"),
            ("eve@example.com", "eve", "password123", "Eve Wilson"),
            ("frank@example.com", "frank", "password123", "Frank Castle"),
            ("grace@example.com", "grace", "password123", "Grace Hopper"),
            ("henry@example.com", "henry", "password123", "Henry Park"),
            ("iris@example.com", "iris", "password123", "Iris West"),
            ("jack@example.com", "jack", "password123", "Jack Ryan"),
            ("kate@example.com", "kate", "password123", "Kate Bishop"),
            ("leo@example.com", "leo", "password123", "Leo Messi"),
            ("mia@example.com", "mia", "password123", "Mia Wallace"),
            ("noah@example.com", "noah", "password123", "Noah Centineo"),
            ("olivia@example.com", "olivia", "password123", "Olivia Benson"),
        ]
        for email, uname, pwd, fname in test_users:
            u = User(email=email, username=uname, hashed_password=get_password_hash(pwd), full_name=fname, is_active=True)
            db.add(u)
            users.append(u)

        await db.flush()

        print("Creating items...")
        all_titles = get_all_titles()
        items = []
        for t in all_titles:
            genres_list = GENRES_MAP[t["category"]]
            selected_genres = random.sample(genres_list, k=random.randint(1, 3))
            avg_rating = round(random.uniform(2.5, 5.0), 1)
            rating_count = random.randint(10, 5000)
            popularity = round(random.uniform(0.1, 1.0), 3)

            item = Item(
                title=t["title"],
                description=f"Amazing {t['category'].lower().rstrip('s')} - {t['title']}. A must experience for fans of {', '.join(selected_genres)}.",
                category=t["category"],
                genres=", ".join(selected_genres),
                tags=",".join(selected_genres + [t["category"].lower()]),
                image_url=f"https://picsum.photos/seed/{t['title'].replace(' ', '').lower()}/400/300",
                release_date=datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1500)),
                avg_rating=avg_rating,
                rating_count=rating_count,
                popularity_score=popularity,
            )
            db.add(item)
            items.append(item)

        await db.flush()

        print("Creating ratings...")
        ratings = []
        for user in users:
            num_ratings = random.randint(5, 25)
            rated_items = random.sample(items, k=min(num_ratings, len(items)))
            for item in rated_items:
                rating_val = round(random.uniform(1.0, 5.0), 1)
                r = Rating(user_id=user.id, item_id=item.id, rating=rating_val)
                db.add(r)
                ratings.append(r)

        print("Creating interactions...")
        interaction_types = ["view", "click", "like", "rate", "share", "bookmark", "add_to_cart"]
        for user in users:
            num_interactions = random.randint(10, 40)
            for _ in range(num_interactions):
                item = random.choice(items)
                itype = random.choice(interaction_types)
                weight_map = {"view": 1.0, "click": 1.5, "like": 2.0, "rate": 2.0, "share": 2.0, "bookmark": 2.0, "add_to_cart": 2.5}
                interaction = Interaction(
                    user_id=user.id,
                    item_id=item.id,
                    interaction_type=itype,
                    weight=weight_map.get(itype, 1.0),
                    duration_seconds=random.randint(0, 600),
                )
                db.add(interaction)

        await db.commit()
        print(f"Seed complete: {len(users) + 1} users, {len(items)} items, {len(ratings)} ratings")


if __name__ == "__main__":
    asyncio.run(seed())
