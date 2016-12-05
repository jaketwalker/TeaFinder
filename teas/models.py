"""
    models.py
    Purpose: class objects define db tables and web functionality
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from django.db import models


class TeaTypes(models.Model):
    ID = models.AutoField(primary_key=True)
    TeaType = models.CharField(max_length=25)
    class Meta:
        db_table = "TeaTypes"
    
    def __str__(self):
        return self.TeaType
    
    def pluralize(self):
        return self.TeaType + 's'


class Sources(models.Model):
    ID = models.AutoField(primary_key=True)
    SourceName = models.CharField(max_length=25)
    URL = models.CharField(max_length=100)
    class Meta:
        db_table = "Sources"
    
    def __str__(self):
        return self.SourceName


class Teas(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    TeaTypeID = models.ForeignKey(TeaTypes, on_delete=models.CASCADE, db_column="TeaTypeID")
    Description = models.CharField(max_length=1000)
    LastUpdatedDate = models.CharField(max_length=25)
    class Meta:
        db_table = "Teas"


class TeasSources(models.Model):
    ID = models.AutoField(primary_key=True)
    TeaID = models.ForeignKey(Teas, on_delete=models.CASCADE, db_column="TeaID")
    SourceID = models.ForeignKey(Sources, on_delete=models.CASCADE, db_column="SourceID")
    ProductID = models.CharField(max_length=50)
    CostOz = models.CharField(max_length=100)
    URL = models.CharField(max_length=1000)
    ImageURL = models.CharField(max_length=1000)
    IsAvailable = models.CharField(max_length=1)
    LastUpdatedDate = models.CharField(max_length=25)
    class Meta:
        db_table = "TeasSources"


class TeasSourcesView(models.Model):
    """Model class representing the TeaSourcesView sqlite view"""
    ID = models.AutoField(primary_key=True, db_column="ID")
    TeaID = models.ForeignKey(Teas, on_delete=models.DO_NOTHING, db_column="TeaID")
    TeaName = models.CharField(max_length=100)
    TeaDescription = models.CharField(max_length=1000)
    TeaTypeID = models.ForeignKey(TeaTypes, on_delete=models.DO_NOTHING, db_column="TeaTypeID")
    TeaType = models.CharField(max_length=25)
    SourceName = models.CharField(max_length=25)
    SourceURL = models.CharField(max_length=100)
    ProductURL = models.CharField(max_length=1000)
    ImageURL = models.CharField(max_length=1000)
    CostOz = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = "TeasSourcesView"

    def __str__(self):
        return ', '.join([
            self.TeaType,
            self.TeaName
            ])
    
    def display_copyright_footer(self):
        return "\u00A9 " + self.SourceName
    
    def display_cost(self):
        return "{0:.2f}".format(float(self.CostOz))
        
    def convert_cost_oz_to_float(self):
        return float(self.CostOz)


class Tags(models.Model):
    ID = models.AutoField(primary_key=True)
    TagName = models.CharField(max_length=25)
    class Meta:
        db_table = "Tags"


class TeasTags(models.Model):
    ID = models.AutoField(primary_key=True)
    TeaID = models.ForeignKey(Teas, on_delete=models.CASCADE, db_column="TeaID")
    TagID = models.ForeignKey(Tags, on_delete=models.CASCADE, db_column="TagID")
    class Meta:
        db_table = "TeasTags"
