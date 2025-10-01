from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth.models import User


class Element(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(blank=True, null=True, default='default.png')
    description = models.TextField(verbose_name="Описание")
    formula = models.CharField(verbose_name="Химическая формула")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Элемент"
        verbose_name_plural = "Элементы"
        db_table = "elements"
        ordering = ("pk",)


class Calculation(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Профессор", null=True, related_name='moderator')

    volume = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Расчет расстворимости №" + str(self.pk)

    def get_elements(self):
        return [
            {
                **model_to_dict(item.element),
                'temperature': item.temperature,
                'weight': item.weight
            }
            for item in ElementCalculation.objects.filter(calculation=self)
        ]

    class Meta:
        verbose_name = "Расчет расстворимости"
        verbose_name_plural = "Расчеты расстворимости"
        db_table = "calculations"
        ordering = ('-date_formation',)


class ElementCalculation(models.Model):
    pk = models.CompositePrimaryKey("element_id", "calculation_id")
    element = models.ForeignKey(Element, on_delete=models.DO_NOTHING)
    calculation = models.ForeignKey(Calculation, on_delete=models.DO_NOTHING)
    temperature = models.IntegerField(default=0)
    weight = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "element_calculation"
        ordering = ('pk', )
