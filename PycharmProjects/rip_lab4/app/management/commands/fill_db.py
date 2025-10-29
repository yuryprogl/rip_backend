from django.core.management.base import BaseCommand

from app.calc import calc
from app.models import *
from app.utils import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(2, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}",
                                      last_name=f"user{i}")


def add_elements():
    Element.objects.create(
        name="Карбонат кальция",
        description="Карбонат кальция (химическая формула CaCO₃, также известный как углекислый кальций) – это неорганическое соединение, соль угольной кислоты и кальция, встречающаяся в природе в виде минералов (кальцит, мрамор, известняк, мел) и являющаяся основным компонентом яичной скорлупы и раковин моллюсков. Он нерастворим в воде и этаноле, но растворяется в кислотах.",
        formula="CaCO₃",
        image="1.png"
    )

    Element.objects.create(
        name="Гидроксид меди (II)",
        description="Гидроксид меди(II), или гидроксид меди(II) (формула Cu(OH)₂), представляет собой нерастворимое в воде голубое твердое вещество. Он является слабым основанием и используется в качестве катализатора и для обработки поверхностей металлов. Это соединение образуется при добавлении щелочи к раствору соли меди, например, гидроксида натрия.",
        formula="Cu(OH)₂",
        image="2.png"
    )

    Element.objects.create(
        name="Сульфат бария",
        description="Сульфат бария (химическая формула BaSO₄) — это нерастворимое в воде неорганическое вещество белого цвета, встречающееся в природе как минерал барит. Он отличается высокой химической инертностью, устойчивостью к кислотам и щелочам, а также высокой плотностью. Применяется в медицине как рентгеноконтрастное вещество, в промышленности как наполнитель для пластмасс, каучука и лакокрасочных материалов, а также для производства радиационно-защитных материалов.",
        formula="BaSO₄",
        image="3.png"
    )

    Element.objects.create(
        name="Калийная селитра",
        description="Калийная селитра (нитрат калия, KNO₃) — это водорастворимое азотно-калийное минеральное удобрение, которое также используется в пищевой промышленности как консервант и в производстве пиротехники. Это бесцветное кристаллическое вещество без запаха, хорошо растворимое в воде, которое подходит для корневых и внекорневых подкормок всех видов растений, повышая их устойчивость к болезням и неблагоприятным условиям, а также улучшая качество урожая.",
        formula="KNO₃",
        image="4.png"
    )

    Element.objects.create(
        name="Соляная кислота",
        description="Соляная кислота (химическая формула HCl) — это сильная минеральная кислота, представляющая собой водный раствор хлороводорода. Она является прозрачной или желтоватой жидкостью с резким запахом, едкой и коррозионной. Соляная кислота находит широкое применение в промышленности (химической, металлургической, пищевой), строительстве и быту для очистки, травления и других целей. Она также входит в состав желудочного сока, где играет важную роль в переваривании пищи.",
        formula="HCl",
        image="5.png"
    )

    Element.objects.create(
        name="Хлорид натрия",
        description="Хлорид натрия, или хлористый натрий (NaCl), – это натриевая соль соляной кислоты, также известная как поваренная соль. Это белое кристаллическое вещество с характерным соленым вкусом, которое встречается в природе в виде минерала галита (каменная соль) и является основным компонентом морской воды.",
        formula="NaCl",
        image="6.png"
    )


def add_forecasts():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    elements = Element.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_forecast(status, elements, owner, moderators)

    # add_forecast(1, elements, users[0], moderators)
    add_forecast(2, elements, users[0], moderators)
    add_forecast(3, elements, users[0], moderators)
    add_forecast(4, elements, users[0], moderators)
    add_forecast(5, elements, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_forecast(status, elements, users[0], moderators)


def add_forecast(status, elements, owner, moderators):
    forecast = Forecast.objects.create()
    forecast.status = status

    if status in [3, 4]:
        forecast.moderator = random.choice(moderators)
        forecast.date_complete = random_date()
        forecast.date_formation = forecast.date_complete - random_timedelta()
        forecast.date_created = forecast.date_formation - random_timedelta()
    else:
        forecast.date_formation = random_date()
        forecast.date_created = forecast.date_formation - random_timedelta()

    forecast.volume = 50 * random.randint(5, 20)

    forecast.owner = owner

    for element in random.sample(list(elements), random.randint(1, 3)):
        item = ElementForecast(
            forecast=forecast,
            element=element,
            temperature=10 * random.randint(10, 30),
        )

        if forecast.status == 3:
            item.weight = calc(forecast, item)

        item.save()

    forecast.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_elements()
        add_forecasts()
