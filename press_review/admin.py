#!/usr/local/bin/python
# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import *
from django import forms

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status',)
    list_filter = ('status',)
    #list_editable = ('status',)
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'status', 'date')}),
        (u'Content', {'fields': (('content', 'spin_content'), 'final_content', 'calendar', 'other_news')}),)
    search_fields = ('title', 'status', 'content')

class PhotoInline(admin.TabularInline):
    model = Photo

class ArticleAdmin(admin.ModelAdmin):
    inlines = [PhotoInline,]
    list_display = ('title', 'date', 'date_added', 'newspaper', 'order', 'is_selected')
    list_filter = ('date', 'newspaper', 'author', 'is_selected')
    list_editable = ('date', 'newspaper', 'order', 'is_selected')
    fieldsets = (
        (None, {'fields': ('url',)}),
        (u'Headline', {'fields': ('title', 'headline', 'is_selected')}),
        (u'Infos', {'fields': ('date', 'author', 'newspaper',)}),
        (u'Content', {'fields': ('content',)}),)
    date_hierarchy = 'date'
    ordering = ('-date',)
    search_fields = ('title', 'content')


class ArticleForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        #TODO To be more fast, right now, we have to filter the Article queryset orfering it by month
        wtf = Article.objects.filter(is_selected=True, date__month='12');
        w = self.fields['article'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.title))
        w.choices = choices


class SyntesisAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'order',)
    #list_filter = ('project',)
    fieldsets = (
        (None, {'fields': ('title', 'project',)}),
        (u'Articles', {'fields': ('article',)}),
        (u'Extra', {'fields': ('order',)}),
        (u'Content', {'fields': ('content',)}),
        (u'Summary', {'fields': ('compression', 'summary',)}),
        (u'Spin', {'fields': ('spin_summary',)}),)
    search_fields = ('title', 'content',)
    filter_horizontal = ('article',)
    form = ArticleForm




admin.site.register(Project, ProjectAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Photo)
admin.site.register(Newspaper)
admin.site.register(Syntesis, SyntesisAdmin)
