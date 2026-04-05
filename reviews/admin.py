from django.contrib import admin
from reviews.models import Review, ReviewVote, Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('is_approved', 'is_verified_purchase', 'rating')
    search_fields = ('product__name', 'user__email', 'title')
    actions = ['approve_reviews']
    raw_id_fields = ('product', 'user')

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        from products.utils import update_product_rating
        for review in queryset:
            update_product_rating(review.product)
    approve_reviews.short_description = 'Approve selected reviews'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'question', 'is_active', 'created_at')
    inlines = [AnswerInline]
    raw_id_fields = ('product', 'user')
