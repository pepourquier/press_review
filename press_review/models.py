#!/usr/bin/python
# -*- coding: utf8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from summarizer import *
import ots
import sys
import os

import urllib3
import re

from django.db.models import Q 

from datetime import datetime
# Create your models here.
PROJECT_STATUS = (
    (_(u'started'), _(u'started')),
    (_(u'in progress'), _(u'in progress')),
    (_(u'completed'), _(u'completed')),
    (_(u'canceled'), _(u'canceled')),
)
class Newspaper(models.Model):
    """
    Use this class to scrape news form a newspaper in archives
    """

    title = models.CharField(max_length=100, blank=True, verbose_name=_(u'title'), 
        help_text=_(u'Article title'))
    url = models.URLField(_(u'website'), blank=True)
    slug = models.CharField(_(u'slug'), max_length=150, blank=True)
    
    def __unicode__(self):
        return self.title 
    
class Article(models.Model):
    """
    Add article to the database. Just put the url to save the content with goose extractor
    """

    url = models.URLField(_(u'website'), blank=True)
    title = models.CharField(max_length=100, blank=True, verbose_name=_(u'title'), 
        help_text=_(u'Article title'))
    headline = models.CharField(max_length=500, blank=True, verbose_name=_(u'headline'), 
        help_text=_(u'Article headline'))
    newspaper = models.CharField(max_length=100, blank=True, verbose_name=_(u'newspaper'), 
        help_text=_(u'Newspaper'))
    author = models.CharField(max_length=100, blank=True, verbose_name=_(u'author'), 
        help_text=_(u'author'))
    content = models.TextField(max_length=10000, blank=True, verbose_name=_(u'content'), 
        help_text=_(u'content'))
    date = models.DateField(_(u'published'), blank=True)
    date_added = models.DateTimeField(_(u'added'), auto_now_add=True)
    order = models.IntegerField(verbose_name=_(u'Order'), null=True, blank=True, default=0)
    is_selected = models.NullBooleanField(verbose_name=_(u'selected'))

    def save(self, *args, **kwargs):
        from goose import Goose
        from text.blob import TextBlob
        g = Goose()
        article = g.extract(url=self.url)
        try:
            b = TextBlob(article.title)
            lang = b.detect_language()
        except:
            lang='en'

        g = Goose({'use_meta_language': False, 'target_language':lang, 'paper_class':'soup'})
        if not self.title:
            self.title = article.title
        if not self.newspaper:
            self.newspaper = article.domain
        if not self.content:
            self.content = article.cleaned_text
        try:
            if article.top_image.src:
                layout = Photo()
                #layout.photo = "images/news/"+str(self.id)+".jpg"
                layout.url = article.top_image.src
                layout.article = self
                layout.save() 
        except:
            pass
        super(Article, self).save()

    def __unicode__(self):
        syntesis = Syntesis.objects.all()
        yet = False
        for s in syntesis:
            if self in s.article.all():
                yet = True 
        if yet:
            return 'YET - %s %s' % (self.date, self.title) 
        else:
            return '%s %s' % (self.date, self.title) 


class Photo(models.Model):
    url = models.URLField(_(u'website'), blank=True)
    caption = models.CharField(max_length=100, blank=True, verbose_name=_(u'caption'), 
        help_text=_(u'Photo Caption'))
    photo = models.ImageField(upload_to='images/news/', blank=True)
    article = models.ForeignKey(Article, help_text=_(u'Article'), null=True)

class Project(models.Model):
    """
    A project round up syntesis and all articles related to it.
    The save method create a .odt file.
    """

    title = models.CharField(max_length=100, blank=False, verbose_name=_(u'title'), 
        help_text=_(u'Project title'))
    slug = models.CharField(_(u'slug'), max_length=150, blank=True)
    date = models.DateTimeField(_(u'date'))
    status = models.CharField(blank=False, verbose_name=_(u'status'), 
        help_text=_(u'Contract status'), choices=PROJECT_STATUS, max_length=20, default=_(u'started'))
    content = models.TextField(max_length=50000, blank=True, verbose_name=_(u'content'), 
        help_text=_(u'content'))
    spin_content = models.TextField(max_length=100000, blank=True, verbose_name=_(u'spin_content'), 
        help_text=_(u'spin_content'))
    final_content = models.TextField(max_length=50000, blank=True, verbose_name=_(u'spin_content'), 
        help_text=_(u'final_content'))
    calendar = models.TextField(max_length=50000, blank=True, verbose_name=_(u'calendar'), 
        help_text=_(u'Calendar'))
    other_news = models.TextField(max_length=50000, blank=True, verbose_name=_(u'Other news'), 
        help_text=_(u'Other News'))

    class Meta:
        verbose_name = _(u'projet')
        verbose_name_plural = _(u'projects')
        
    def save(self):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.content:
            content = ''
            syntesis = Syntesis.objects.filter(project=self)
            for s in syntesis:
                content += '\r\r'
                content += s.title + '\r\r'
                content += s.summary + '\r'
            self.content = content
        if not self.spin_content:
            self.spin_content = get_text_synonymizer(self.content)
        if self.final_content != "-":
            from odf.opendocument import OpenDocumentText
            from odf.style import Style, TextProperties, ParagraphProperties 
            from odf import text

            #TODO Automatize the table of content creation
            from odf.text import P, TableOfContent, TableOfContentSource, TocMark

            textdoc = OpenDocumentText()

            tc = text.TableOfContent(name="Table of contents") 
            tcs = text.TableOfContentSource() 
            tc.addElement(tcs) 


            heading1 = Style(name="Heading 1", family="paragraph")
            heading1.addElement(TextProperties(fontfamily="Cambria", fontweight="bold", fontsize="20pt", color="#4F81BD"))
            textdoc.styles.addElement(heading1)
            
            content1 = Style(name="Content 1", family="paragraph")
            content1.addElement(ParagraphProperties(textalign="justify", lineheight="0.60cm"))
            content1.addElement(TextProperties(fontfamily="Times New Roman", fontsize="12pt"))
            textdoc.styles.addElement(content1)
            
            heading2 = Style(name="Heading 2", family="paragraph")
            heading2.addElement(TextProperties(fontfamily="Cambria", fontsize="26pt", color="#17365d"))
            textdoc.styles.addElement(heading2)
            
            source1 = Style(name="Source 1", family="paragraph")
            source1.addElement(ParagraphProperties(textalign="right"))
            source1.addElement(TextProperties(fontfamily="Times New Roman", fontweight='italic', fontsize="12pt"))
            textdoc.styles.addElement(source1)

            textdoc.text.addElement(P(stylename=heading1, text="I/ Presse review :"))
            #articles = Article.objects.filter(Q(date__month = self.date.month))
            syntesis = Syntesis.objects.filter(project=self)
            textdoc.text.addElement(P(text='\r\n'))
            for s in syntesis:
                for a in s.article.all():
                    textdoc.text.addElement(P(stylename=heading2, text=a.title), TocMark(outlinelevel="2", stringvalue=a.title))
                    textdoc.text.addElement(P(text='\r\n'))
                    content = unicode(a.content).split('\r\n\r\n')
                    for c in content:
                        textdoc.text.addElement(P(stylename=content1, text=unicode(c)))
                        textdoc.text.addElement(P(text='\r\n'))
                    textdoc.text.addElement(P(text='\r\n'))
                    if a.author:
                        author = ' by '+unicode(a.author)
                    else: 
                        author = ''
                    textdoc.text.addElement(P(stylename=source1, text='In '+unicode(a.newspaper)+author+'. Published the '+unicode(a.date)))
                    textdoc.text.addElement(P(text='\r\n'))
                    textdoc.text.addElement(P(text='\r\n'))
            
            textdoc.text.addElement(tc)
            
            textdoc.text.addElement(P(stylename=heading1, text="II/ Summary"))
            content = self.final_content.split('\r\n\r\n')
            for c in content:
                textdoc.text.addElement(P(stylename=content1, text=unicode(c)))
                textdoc.text.addElement(P(text='\r\n'))
            textdoc.text.addElement(P(text='\r\n'))
            textdoc.text.addElement(P(stylename=heading1, text="III/ Agenda"))
            calendar = self.calendar.split('\r\n')
            for c in calendar:
                textdoc.text.addElement(P(stylename=content1, text=unicode(c)))
            textdoc.text.addElement(P(text='\r\n'))
            textdoc.text.addElement(P(stylename=heading1, text="IV/ Other information"))
            reports = self.other_news.split('\r\n')
            for c in reports:
                textdoc.text.addElement(P(stylename=content1, text=unicode(c)))
            textdoc.save(str(self.slug), True)

        super(Project, self).save()

    def __unicode__(self):
        return self.title


class Syntesis(models.Model):
    """
    Select all the articles you need in this syntesis to write un summary.
    Choose compression between 0 and 100 to define the compression level.
    """

    title = models.CharField(max_length=100, blank=False, verbose_name=_(u'title'), 
        help_text=_(u'Project title'))
    article = models.ManyToManyField(Article, verbose_name=_(u'articles'))
    content = models.TextField(max_length=10000, blank=True, verbose_name=_(u'content'), 
        help_text=_(u'content'))
    summary = models.TextField(max_length=10000, blank=True, verbose_name=_(u'summary'), 
        help_text=_(u'summary'))
    spin_summary = models.TextField(max_length=10000, blank=True, verbose_name=_(u'spin_summary'), 
        help_text=_(u'spin_summary'))
    compression = models.IntegerField(verbose_name=_(u'Compression'), default=20)
    order = models.IntegerField(verbose_name=_(u'Order'), null=True, default=0)
    project = models.ForeignKey(Project, help_text=_(u'Project'), null=True)
    date_added = models.DateTimeField(_(u'added'), auto_now_add=True)
    
    def __unicode__(self):
        return self.title
        
    def save(self):
        if not self.content:
            articles = self.article.all()
            content = ''
            for a in articles:
                content += a.content + '\r'
            self.content = content
            content = content.replace(u'–', '-')
            content = content.replace(u'“', '"')
            content = content.replace(u'”', '"')
            content = content.replace(u'’', "'")
            content = content.replace('[\d]', "")
        if not self.summary:
            self.summary = get_summary(self.content, self.compression)
            from text.blob import TextBlob
            try:
                b = TextBlob(self.content.split('\n', 1)[0])
                lang = b.detect_language()
            except:
                lang='en'
            
            o = ots.OTS(lang, self.compression)
            filename = u'text'+str(self.id)+'.txt'
            f = open(filename, 'w')
            f.write(self.content.encode("utf-8"))
            f.close()
            o.parse(filename, 60)
            try: 
                os.remove(filename)
            except:
                pass
            self.summary = str(o)
        if not self.spin_summary:
            self.spin_summary = get_text_synonymizer(self.summary)
        super(Syntesis, self).save()
