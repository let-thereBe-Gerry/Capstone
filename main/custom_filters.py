from django import template

register = template.Library()

@register.filter
def rating_stars(value):
    value = int(value)
    return '😍' * value

@register.filter
def average_rating_stars(reviews):
    if not reviews:
        return 'No reviews yet'

    total_ratings = sum([review.rate for review in reviews])
    average_rating = round(total_ratings / len(reviews), 2)  # Round to two decimal places

    return '😍' * int(average_rating) + '🟡' * int(5 - average_rating)

@register.filter
def numeric_average_rating(reviews):
    if not reviews:
        return 'No reviews yet'

    total_ratings = sum([review.rate for review in reviews])
    average_rating = round(total_ratings / len(reviews), 2)  # Round to two decimal places

    return average_rating