---
layout: default
title: XML-схема
nav_order: 16
has_children: true
child_nav_order: desc
---

# XML-схема печатной формы
{: .no_toc }

<details open markdown="block">
  <summary>
    Содержание
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Описание

> Начиная с версии 2025.2 для формирования печатных форм, а также для обмена данными используется унифицированная XML-схема печатной формы.

Макеты PrintWizard экспортируются и импортируются в формате XML, соответствующем схеме версии **6.1** (`http://printwizard.ru/export/v6.1`). Эта страница описывает структуру XML и допустимые значения перечислений.
{: .fs-6 .fw-300 }

## Структура документа

XML-файл макета содержит единственный корневой элемент `Template` со всеми вложенными коллекциями:

```
Template
├── Attributes              — реквизиты макета (название, флаги)
├── Properties[]            — произвольные свойства (ключ–значение)
├── Objects[]               — объекты метаданных 1С
│     └── Command           — настройка команды печати
├── Queries[]               — запросы к данным
│     └── Fields[]          — поля запроса
├── Datasets[]              — наборы данных
│     ├── Source            — источник данных
│     └── Fields[]          — поля набора
├── Joins[]                 — соединения наборов
│     └── Fields[]          — пары полей соединения
├── Parameters[]            — входные параметры печати
├── PrintParameters[]       — параметры страницы (поля, ориентация…)
├── Areas[]                 — области шаблона
│     └── Parameters[]      — параметры ячеек (привязка к данным)
├── Events[]                — обработчики событий жизненного цикла
├── Functions[]             — пользовательские функции
│     └── Parameters[]      — параметры функции
├── AvailableFields[]       — вычисляемый список доступных полей
├── DataLinks[]             — связи между таблицами схемы
├── PrintTemplate           — шаблон (base64: MXL или XLSX/DOCX)
└── Variants[]              — варианты печати
      ├── PrintParameters[]
      ├── Areas[]
      ├── Events[]
      └── PrintTemplate
```

---

## Template

Корневой элемент макета.

```xml
<Template pw_type="Template"
          Key="e7a1c3b2-..."
          Name="РеализацияТоваровУслуг">

  <Attributes IsRegistry="false" IsOfficeOpenXML="false">
    <Presentation>Счёт на оплату</Presentation>
    <Description>Счёт на оплату покупателю</Description>
  </Attributes>

  <Objects>...</Objects>
  <Queries>...</Queries>
  <Datasets>...</Datasets>
  <Parameters>...</Parameters>
  <Areas>...</Areas>
  <AvailableFields>...</AvailableFields>

</Template>
```

| Атрибут | Обязателен | Описание |
|---|---|---|
| `Key` | ✅ | Уникальный идентификатор макета (UUID) |
| `Name` | | Внутреннее имя макета |
| `pw_type` | | Всегда `Template` |

### Template / Attributes

| Атрибут / Элемент | Обязателен | Описание |
|---|---|---|
| `IsRegistry` | ✅ | Макет является реестром (многострочный список) |
| `IsOfficeOpenXML` | ✅ | Шаблон в формате Office Open XML (DOCX/XLSX) |
| `ExtKey` | | Внешний ключ для интеграции |
| `<Presentation>` | ✅ | Краткое наименование (отображается в списке) |
| `<Description>` | | Полное наименование |
| `<Code>` | | Уникальный код макета |
| `<Comment>` | | Комментарий разработчика |

---

## Objects — объекты метаданных

Каждый элемент `Objects` описывает объект 1С, для которого создана печатная форма.

```xml
<Objects pw_type="Object"
         Number="1"
         Key="a1b2c3d4-..."
         Kind="Документы"
         Name="РеализацияТоваровУслуг"
         FullName="Документы.РеализацияТоваровУслуг"
         UseCommand="true">
  <Command Id="print_cmd_1" Order="1"
           Presentation="Счёт на оплату"
           CheckPosting="false"
           SkipPreview="false"/>
</Objects>
```

| Атрибут | Описание |
|---|---|
| `Kind` | Вид коллекции метаданных — см. [перечисление](#kind-вид-объекта) |
| `FullName` | Полное имя: `Документы.РеализацияТоваровУслуг` |
| `UseCommand` | Создавать команду в меню «Печать» |

---

## Queries — запросы

Запрос содержит текст на языке запросов 1С и список полей результата.

```xml
<Queries pw_type="Query"
         Number="1"
         Key="b2c3d4e5-..."
         Name="QueryGoods"
         ResultType="ValueTable"
         TempTable=""
         Invalid="false"
         NotFilterByRef="false">
  <Text>ВЫБРАТЬ
    Строки.Номенклатура КАК Номенклатура,
    Строки.Количество  КАК Количество,
    Строки.Сумма       КАК Сумма
  ИЗ Документы.РеализацияТоваровУслуг.Товары КАК Строки
  ГДЕ Строки.Ссылка В (&МассивОбъектов)</Text>
  <Errors/>
  <Guidelines/>
  <Fields>
    <Fields pw_type="Query.Field" Key="c1-..." Name="Номенклатура" Field="Номенклатура"/>
    <Fields pw_type="Query.Field" Key="c2-..." Name="Количество"   Field="Количество"/>
    <Fields pw_type="Query.Field" Key="c3-..." Name="Сумма"        Field="Сумма"/>
  </Fields>
</Queries>
```

| Атрибут | Описание |
|---|---|
| `ResultType` | `ValueTable` — обычный запрос; `TempTable` — временная таблица |
| `TempTable` | Имя временной таблицы (если `ResultType = TempTable`) |
| `Invalid` | `true` если в запросе обнаружены ошибки |
| `NotFilterByRef` | Не применять стандартный отбор по ссылке объекта |

---

## Datasets — наборы данных

Набор данных связывает запрос с областью шаблона и описывает состав полей.

```xml
<Datasets pw_type="Dataset"
          Number="1"
          Key="d1e2f3a4-..."
          Name="DSGoods"
          Type="Collection"
          SourceType="Query"
          UseInTemplate="true">
  <Source pw_type="DataSource" Type="Query" QueryKey="b2c3d4e5-..."/>
  <Fields>
    <Fields pw_type="Dataset.Field" Key="f1-..." Name="Номенклатура" Type="Dataset"/>
    <Fields pw_type="Dataset.Field" Key="f2-..." Name="Количество"   Type="Dataset"/>
    <Fields pw_type="Dataset.Field" Key="f3-..." Name="НомерСтроки"  Type="Numerator"/>
  </Fields>
</Datasets>
```

| Атрибут | Описание |
|---|---|
| `Type` | Тип набора — см. [перечисление](#datasettype-тип-набора) |
| `SourceType` | `Query` / `Object` / `Algorithm` |
| `UseInTemplate` | Использовать поля набора в шаблоне |

### Dataset.Field — типы полей

| Значение `Type` | Описание |
|---|---|
| `Dataset` | Поле из запроса или источника данных |
| `Description` | Составное строковое представление (несколько реквизитов в одной ячейке) |
| `Numerator` | Автоматическая нумерация строк |
| `Algorithm` | Вычисляемое поле (код на 1С) |
| `Attribute` | Дополнительное свойство объекта (БСП) |
| `ContactInfo` | Контактная информация (БСП) |
| `Function` | Пользовательская функция макета |
| `QRCode` | QR-код |

---

## Areas — области шаблона

Область соответствует именованному диапазону строк в шаблоне и определяет способ вывода данных.

```xml
<Areas pw_type="Area"
       Number="1"
       Key="e1f2a3b4-..."
       Name="Header"
       PrintMethod="Single"
       DatasetKey="..."
       Order="1">
  <Parameters>
    <Parameters pw_type="Area.Parameter"
                Key="p1-..."
                Name="Контрагент"
                Type="Dataset"
                IsPicture="false"
                IsDetails="false">
      <Value pw_type="Field.Dataset"
             DatasetKey="..."
             DatasetFieldKey="..."
             DatasetFieldName="Контрагент"
             IsRowField="false"/>
      <Presentation/>
    </Parameters>

    <Parameters pw_type="Area.Parameter"
                Key="p2-..."
                Name="ИтогоПрописью"
                Type="SumInWords"
                IsPicture="false"
                IsDetails="false">
      <Value pw_type="Field.SumInWords">
        <NumberField pw_type="Field.Dataset"
                     DatasetKey="..." DatasetFieldKey="..."
                     DatasetFieldName="СуммаДокумента"/>
        <CurrencyDefault>RUB</CurrencyDefault>
        <NoFractions>false</NoFractions>
        <FormatString/>
        <Parameters/>
      </Value>
      <Presentation/>
    </Parameters>
  </Parameters>
</Areas>
```

| Атрибут | Описание |
|---|---|
| `PrintMethod` | Способ вывода — см. [перечисление](#areamethod-способ-вывода) |
| `PrintSettings` | Дополнительная настройка — см. [перечисление](#areasettings-настройка-вывода) |
| `DatasetKey` | Ключ связанного набора данных (обязателен для `Collection`) |
| `Order` | Порядок вывода области |

### Area.Parameter — типы привязки ячейки

| Значение `Type` | Описание | Тип значения `<Value>` |
|---|---|---|
| `Dataset` | Поле из набора данных | `Field.Dataset` |
| `Description` | Составное представление | `Field.Description` |
| `Algorithm` | Произвольный код 1С | `Field.Function` |
| `SumInWords` | Сумма прописью | `Field.SumInWords` |
| `QRCode` | QR-код | `Field.QRCode` |

---

## AvailableFields — доступные поля

Вычисляемая коллекция, описывающая все поля, доступные для вставки в параметры областей. Формируется автоматически при загрузке схемы.

```xml
<AvailableFields pw_type="AvailableField"
                 Key="af1-..."
                 Path="НаборыДанных.DSGoods.Строка.Номенклатура"
                 DatasetKey="d1e2f3a4-..."
                 DatasetFieldKey="f1-..."
                 DatasetFieldName="Номенклатура"
                 IsRowField="true">
  <Presentation>Номенклатура</Presentation>
  <Datatypes>СправочникСсылка.Номенклатура</Datatypes>
</AvailableFields>
```

Пути строятся по следующим шаблонам:

| Тип набора | Шаблон пути |
|---|---|
| `FirstRow` / `LastRow` / `Concatenation` | `НаборыДанных.[Набор].[Поле]` |
| `Collection` — поле строки | `НаборыДанных.[Набор].Строка.[Поле]` |
| `Collection` — итог | `НаборыДанных.[Набор].Итог.[Поле]` |
| `Collection` — количество строк | `НаборыДанных.[Набор].КоличествоСтрок` |
| Через соединение | `НаборыДанных.[Набор].[Соединение].[Поле]` |

---

## Перечисления

### Kind — вид объекта

Допустимые значения атрибута `Kind` у элемента `Objects`:

`Справочники` · `Документы` · `БизнесПроцессы` · `Задачи` · `РегистрыБухгалтерии` · `РегистрыСведений` · `РегистрыНакопления` · `ПланыСчетов` · `ПланыВидовХарактеристик` · `Перечисления` · `Константы` · `КритерииОтбора` · `ЖурналыДокументов` · `ПланыОбмена` · `ПланыВидовРасчета` · `РегистрыРасчета` · `Перерасчеты` · `ВнешниеИсточникиДанных` · `НумераторыДокументов` · `Последовательности`

---

### Dataset.Type — тип набора

| Значение | Описание |
|---|---|
| `FirstRow` | Берётся только первая строка результата |
| `LastRow` | Берётся только последняя строка |
| `Concatenation` | Строки объединяются в одно значение |
| `Collection` | Многострочная коллекция — цикл по каждой строке |

---

### Area.Method — способ вывода

| Значение | Описание |
|---|---|
| `Single` | Без повторений — вывести один раз |
| `Collection` | По строкам коллекции — цикл по набору |
| `Header` | Верхний колонтитул (повторяется на каждой странице) |
| `Footer` | Нижний колонтитул (повторяется на каждой странице) |
| `Wrap` | Перенос строки |
| `Skip` | Не выводить |
| `Column` | Колонка |
| `ControlRow` | Контрольная строка |
| `WrapRow` | Строка переноса |
| `Empty` | Пустая область |

---

### Area.Settings — настройка вывода

| Значение | Описание |
|---|---|
| `NewSection` | Начать новый раздел (разрыв страницы перед областью) |
| `RepeatInHeader` | Повторять в шапке каждой страницы |
| `RepeatInFooter` | Повторять в подвале каждой страницы |
| `CheckPrint` | Проверять необходимость вывода перед выводом области |

---

### QRCode.Type — тип QR-кода

| Значение | Описание |
|---|---|
| `Bank` | УФЭБС (стандарт быстрого платежа) |
| `XML` | Произвольный XML |
| `JSON` | Произвольный JSON |
| `Algorithm` | Произвольный алгоритм на 1С |

---

### Event.Name — события жизненного цикла

| Значение | Когда срабатывает |
|---|---|
| `BeforeInitialization` | Перед инициализацией макета |
| `OnDataReceiving` | При получении данных |
| `BeforeFormation` | Перед началом формирования |
| `BeforePageOutput` | Перед выводом каждой страницы |
| `BeforeAreaOutput` | Перед выводом каждой области |
| `AfterAreaOutput` | После вывода области |
| `AfterPageOutput` | После вывода страницы |
| `AfterFormation` | После завершения формирования |

---

### Query.ResultType — тип результата запроса

| Значение | Описание |
|---|---|
| `ValueTable` | Обычный запрос, результат используется как набор данных |
| `TempTable` | Временная таблица — промежуточный результат для других запросов |

---

### Parameter.Type — тип входного параметра

| Значение | Описание |
|---|---|
| `Value` | Единственное значение |
| `List` | Список значений |
| `Table` | Таблица значений |
| `Algorithm` | Вычисляется алгоритмом |