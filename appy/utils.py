from collections import defaultdict

from appy.models import Application
from appy.models import Position
from appy.models import Tag


def apply_for_position(position, user):
    app = Application(user=user, position=position)
    app.save()


def search_positions(company, job_title, tag_search):
    positions = Position.objects.all()
    if company:
        positions = positions.filter(company__icontains=company)
    if job_title:
        positions = positions.filter(job_title__icontains=job_title)
    if tag_search:
        p_ids = set()
        tags = Tag.objects.filter(description__icontains=tag_search)
        for tag in tags:
            for p in tag.position_set.all():
                p_ids.add(p.id)
        positions = positions.filter(id__in=p_ids)

    return positions


def sort_positions(positions, user):
    if Application.objects.filter(user=user).count() < 3:
        return positions.order_by('-created_at')

    user_weightings = get_weighting_dict(user)
    return sorted(positions, key=lambda pos: recommendation_score(pos, user_weightings), reverse=True)


def get_weighting_dict(user):
    user_applications = Application.objects.filter(user=user).prefetch_related('position__tags')
    successful_applications = user_applications.filter(status=Application.NEGOTIATING)
    rejected_applications = user_applications.filter(status=Application.REJECTED)
    neutral_applications = user_applications.exclude(status__in=(Application.NEGOTIATING, Application.REJECTED))

    qs_weightings = {
        successful_applications: 2,
        rejected_applications: -1,
        neutral_applications: 1,
    }

    weighting_dict = defaultdict(int)
    for qs, weighting in qs_weightings.items():
        weighting_dict = update_weighting_dict(qs, weighting, weighting_dict)
    return weighting_dict


def update_weighting_dict(qs, weighting, weighting_dict):
    for app in qs:
        tags = app.position.tags.all()
        for t in tags:
            weighting_dict[t.description] += weighting
    return weighting_dict


def recommendation_score(position, weighting_dict):
    score = 0
    tags = position.tags.all()
    num_tags = len(tags)
    for t in tags:
        score += weighting_dict[t.description]
    return num_tags