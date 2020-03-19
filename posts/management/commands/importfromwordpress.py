from django.core.management.base import BaseCommand, CommandError
from posts.models import Post, Tag, Category, Profile
import MySQLdb
from MySQLdb.constants import FIELD_TYPE
import pytz
import datetime

class Command(BaseCommand):
    help = 'Imports WordPress posts'

    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('user')
        parser.add_argument('passwd')
        parser.add_argument('db')
        parser.add_argument('wp-table-prefix')


    def handle(self, *args, **options):
        self.stdout.write('Importing WordPress posts')
        wp_table_prefix = options['wp-table-prefix']
        utc = pytz.utc

        my_conv = {
            FIELD_TYPE.LONG: int,
            FIELD_TYPE.INT24: int,
            FIELD_TYPE.SHORT: int,
            FIELD_TYPE.TINY: int,
            FIELD_TYPE.LONGLONG: int,
            FIELD_TYPE.DATETIME: str,
        }

        try: 
            db = MySQLdb.connect(
                host=options['host'], 
                user=options['user'], 
                passwd=options['passwd'], 
                db=options['db'],
                conv=my_conv,
                use_unicode=True,
                charset='utf8mb4')
        except Exception as e:
            self.stderr.write('Unable to connect to database')
            self.stderr.write(str(e))
            return

        cur = db.cursor()

        cur.execute('SET NAMES utf8mb4')
        cur.execute("SET CHARACTER SET utf8mb4")
        cur.execute("SET character_set_connection=utf8mb4")

        wpTagMap = dict()
        wpCategoryMap = dict()
        posts = list()

        # GET TAGS
        self.stdout.write('Migrating Tags')

        cur.execute(f"""SELECT COUNT(*) 
            FROM {wp_table_prefix}_terms AS terms 
            INNER JOIN {wp_table_prefix}_term_taxonomy AS taxonomy 
                ON terms.term_id = taxonomy.term_id 
            INNER JOIN {wp_table_prefix}_term_relationships AS relationships
                ON relationships.`term_taxonomy_id` = taxonomy.`term_taxonomy_id`
            INNER JOIN {wp_table_prefix}_posts AS posts
                ON relationships.`object_id` = posts.`ID`
            WHERE taxonomy.taxonomy = 'post_tag'
                AND posts.post_type = 'post'""")
        row = cur.fetchone()
        self.stdout.write(f"{row[0]} tags to migrate")

        cur.execute(f"""SELECT 
                terms.term_id, 
                terms.name, 
                terms.slug, 
                posts.ID
            FROM {wp_table_prefix}_terms AS terms 
            INNER JOIN {wp_table_prefix}_term_taxonomy AS taxonomy 
                ON terms.term_id = taxonomy.term_id 
            INNER JOIN {wp_table_prefix}_term_relationships AS relationships
                ON relationships.`term_taxonomy_id` = taxonomy.`term_taxonomy_id`
            INNER JOIN {wp_table_prefix}_posts AS posts
                ON relationships.`object_id` = posts.`ID`
            WHERE taxonomy.taxonomy = 'post_tag'
                AND posts.post_type = 'post'""")

        rows = cur.fetchall()

        savedTags = dict()

        for row in rows:
            tag = Tag(name = row[1], slug = row[2])

            if row[0] in savedTags:
                tag = savedTags[row[0]]
            else:
                tag.save()
                savedTags[row[0]] = tag

            if row[3] not in wpTagMap:
                wpTagMap[row[3]] = list()

            wpTagMap[row[3]].append(tag)

        self.stdout.write(f"{len(wpTagMap)} tags migrated")


        

        # GET CATEGORIES
        self.stdout.write('Migrating Categories')
        cur.execute(f"""SELECT COUNT(*) 
            FROM {wp_table_prefix}_terms AS terms 
            INNER JOIN {wp_table_prefix}_term_taxonomy AS taxonomy 
                ON terms.term_id = taxonomy.term_id 
            INNER JOIN {wp_table_prefix}_term_relationships AS relationships
                ON relationships.`term_taxonomy_id` = taxonomy.`term_taxonomy_id`
            INNER JOIN {wp_table_prefix}_posts AS posts
                ON relationships.`object_id` = posts.`ID`
            WHERE taxonomy.taxonomy = 'category'
                AND posts.post_type = 'post'""")
        row = cur.fetchone()
        self.stdout.write(f"{row[0]} categories to migrate")

        cur.execute(f"""SELECT 
                terms.term_id, 
                terms.name, 
                terms.slug, 
                posts.ID 
            FROM {wp_table_prefix}_terms AS terms 
            INNER JOIN {wp_table_prefix}_term_taxonomy AS taxonomy 
                ON terms.term_id = taxonomy.term_id 
            INNER JOIN {wp_table_prefix}_term_relationships AS relationships
                ON relationships.`term_taxonomy_id` = taxonomy.`term_taxonomy_id`
            INNER JOIN {wp_table_prefix}_posts AS posts
                ON relationships.`object_id` = posts.`ID`
            WHERE taxonomy.taxonomy = 'category'
                AND posts.post_type = 'post'""")

        rows = cur.fetchall()

        savedCategories = dict()

        for row in rows:
            category = Category(name = row[1], slug = row[2])

            if row[0] in savedCategories:
                category = savedCategories[row[0]]
            else:
                category.save()
                savedCategories[row[0]] = category

            wpCategoryMap[row[3]] = category

        self.stdout.write(f"{len(wpCategoryMap)} categories migrated")


        # POSTS
        self.stdout.write('Migrating Posts')
        cur.execute(f"SELECT COUNT(*) FROM {wp_table_prefix}_posts WHERE post_type = 'post'")
        row = cur.fetchone()
        self.stdout.write(f"{row[0]} posts to migrate")

        # we need a default Author
        author = Profile.objects.all()[:1].get()
        self.stdout.write(f'Default author is {author.name}')

        cur.execute(f"SELECT ID, post_date_gmt, post_content, post_title, post_excerpt, post_status, post_name, post_modified_gmt FROM {wp_table_prefix}_posts WHERE post_type = 'post'")

        rows = cur.fetchall()

        for row in rows:
            if not row[6]:
                self.stdout.write(f'{row[3]} has no slug. Skipping.')
                continue

            published = row[1]
            if published == '0000-00-00 00:00:00':
                published = None
            else:
                published = utc.localize(datetime.datetime.strptime(published, "%Y-%m-%d %H:%M:%S"), is_dst=None)

            updated = row[7]
            if updated == '0000-00-00 00:00:00':
                updated = None
            else:
                updated = utc.localize(datetime.datetime.strptime(updated, "%Y-%m-%d %H:%M:%S"), is_dst=None)

            post = Post(
                published=published,
                content=row[2],
                title=row[3],
                summary=row[4],
                is_published=row[5] == 'publish',
                slug=row[6],
                updated=updated,
                author=author)
            
            try:
                post.save()
            except Exception as e:
                self.stderr.write(str(e))
                self.stderr.write(post.name)
                raise e
            posts.append({
                'post': post,
                'wpId': row[0]
            })

        self.stdout.write(f"{len(posts)} posts migrated")

        # Attaching Tags and Categories
        self.stdout.write("Attaching tags and categories")
        for post in posts:
            if post['wpId'] in wpCategoryMap:
                post['post'].category = wpCategoryMap[post['wpId']]
            else:
                self.stdout.write(f"No category for {post['post'].title}")            

            if post['wpId'] in wpTagMap:
                post['post'].tags.set(wpTagMap[post['wpId']])
            else:
                self.stdout.write(f"No tags for {post['post'].title}")            
            
            post['post'].save()

        self.stdout.write("Tags and categories attached")


        cur.close()
        db.close()
        self.stdout.write('WordPress posts imported')
        return