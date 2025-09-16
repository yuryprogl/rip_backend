from django.shortcuts import render

elements_mock = [
    {
        "id": 1,
        "name": "Карбонат кальция",
        "description": "Карбонат кальция (химическая формула CaCO₃, также известный как углекислый кальций) – это неорганическое соединение, соль угольной кислоты и кальция, встречающаяся в природе в виде минералов (кальцит, мрамор, известняк, мел) и являющаяся основным компонентом яичной скорлупы и раковин моллюсков. Он нерастворим в воде и этаноле, но растворяется в кислотах.",
        "formula": "CaCO₃",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Гидроксид меди (II)",
        "description": "Гидроксид меди(II), или гидроксид меди(II) (формула Cu(OH)₂), представляет собой нерастворимое в воде голубое твердое вещество. Он является слабым основанием и используется в качестве катализатора и для обработки поверхностей металлов. Это соединение образуется при добавлении щелочи к раствору соли меди, например, гидроксида натрия.",
        "formula": "Cu(OH)₂",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Сульфат бария",
        "description": "Сульфат бария (химическая формула BaSO₄) — это нерастворимое в воде неорганическое вещество белого цвета, встречающееся в природе как минерал барит. Он отличается высокой химической инертностью, устойчивостью к кислотам и щелочам, а также высокой плотностью. Применяется в медицине как рентгеноконтрастное вещество, в промышленности как наполнитель для пластмасс, каучука и лакокрасочных материалов, а также для производства радиационно-защитных материалов. ",
        "formula": "BaSO₄",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Калийная селитра",
        "description": "Калийная селитра (нитрат калия, KNO₃) — это водорастворимое азотно-калийное минеральное удобрение, которое также используется в пищевой промышленности как консервант и в производстве пиротехники. Это бесцветное кристаллическое вещество без запаха, хорошо растворимое в воде, которое подходит для корневых и внекорневых подкормок всех видов растений, повышая их устойчивость к болезням и неблагоприятным условиям, а также улучшая качество урожая. ",
        "formula": "KNO₃",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Соляная кислота",
        "description": "Соляная кислота (химическая формула HCl) — это сильная минеральная кислота, представляющая собой водный раствор хлороводорода. Она является прозрачной или желтоватой жидкостью с резким запахом, едкой и коррозионной. Соляная кислота находит широкое применение в промышленности (химической, металлургической, пищевой), строительстве и быту для очистки, травления и других целей. Она также входит в состав желудочного сока, где играет важную роль в переваривании пищи. ",
        "formula": "HCl",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Хлорид натрия",
        "description": "Описание",
        "formula": "NaCl",
        "image": "http://localhost:9000/images/6.png"
    }
]

calculations_mock = [
    {
        "id": 1,
        "status": "Черновик",
        "date_created": "10 сентября 2025г",
        "field": "123",
        "elements": [
            {
                "id": 1,
                "concentration": 2
            },
            {
                "id": 2,
                "concentration": 4
            },
            {
                "id": 3,
                "concentration": 1
            }
        ]
    },
    {
        "id": 2,
        "status": "В работе",
        "date_created": "5 сентября 2025г",
        "field": "123",
        "elements": [
            {
                "id": 1,
                "concentration": 3
            },
            {
                "id": 3,
                "concentration": 2
            }
        ]
    },
    {
        "id": 3,
        "status": "Завершена",
        "date_created": "10 августа 2025г",
        "field": "123",
        "elements": [
            {
                "id": 2,
                "concentration": 4
            }
        ]
    }
]


def get_element(element_id):
    for element in elements_mock:
        if element["id"] == element_id:
            return element


def get_elements():
    return elements_mock


def search_elements(element_name):
    res = []

    for element in elements_mock:
        if element_name.lower() in element["name"].lower():
            res.append(element)

    return res


def get_draft_calculation():
    for calculation in calculations_mock:
        if calculation["status"] == "Черновик":
            return calculation


def get_calculation(calculation_id):
    for calculation in calculations_mock:
        if calculation["id"] == calculation_id:
            return calculation


def index(request):
    element_name = request.GET.get("element_name", "")
    elements = search_elements(element_name) if element_name else get_elements()
    draft_calculation = get_draft_calculation()

    context = {
        "elements": elements,
        "element_name": element_name,
        "elements_count": len(draft_calculation["elements"]),
        "draft_calculation": draft_calculation
    }

    return render(request, "elements_page.html", context)


def element_page(request, element_id):
    context = {
        "element": get_element(element_id),
    }

    return render(request, "element_page.html", context)


def calculation_page(request, calculation_id):
    calculation = get_calculation(calculation_id)
    elements = [
        {**get_element(element["id"]), "concentration": element["concentration"]}
        for element in calculation["elements"]
    ]

    context = {
        "calculation": calculation,
        "elements": elements
    }

    return render(request, "calculation_page.html", context)
