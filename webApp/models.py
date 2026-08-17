from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
class Content(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    #content = models.CharField(max_length=255, verbose_name="Контент")
    content = CKEditor5Field('Контент', config_name='extends')
    idcard = models.CharField(max_length=255, verbose_name="Карта")
    idmenu = models.CharField(max_length=255, verbose_name="Меню")             
    author = models.CharField(max_length=255, verbose_name="Автор поста")
    date = models.CharField(max_length=255, verbose_name="Дата поста")
    def __str__(self):
        return self.title
#class SecondModel(models.Model):
    # Поля вашей модели
#    field1 = models.CharField(max_length=100)
#    field2 = models.CharField(max_length=100)
    #class Meta:
        # Указывает, что эта модель использует вторую базу данных
    #    using = 'mysql_db'
        # Если вы хотите указать имя таблицы в базе данных
    #    db_table = 'table_ericsson_2g_v'