class Podcast:
    def __init__(self, title, url, transcript):
        self.title = title
        self.url = url
        self.transcript = transcript
        
    def get_podcast_from_db(db_manager, podcast_name):
        query = 'SELECT Title, URL, Transcript FROM dbo.Podcasts WHERE Podcast = ?'
        results = db_manager.execute_query(query, podcast_name)
        podcasts = [Podcast(result[0], result[1], result[2]) for result in results]
        return podcasts