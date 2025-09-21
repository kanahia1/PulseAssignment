class Article:
    def __init__(self, title, description, rating, date, reviewer):
        self.title = title
        self.description = description
        self.rating = rating
        self.date = date
        self.reviewer = reviewer

    def __repr__(self):
        return (f"Article(title='{self.title}', "
                f"description={self.description}, "
                f"rating={self.rating}, "
                f"date='{self.date}', "
                f"reviewer='{self.reviewer}')")