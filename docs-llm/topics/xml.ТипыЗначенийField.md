# Типы значений Field.*

Каждый параметр области (`Area.Parameter`) и поле набора данных содержат элемент `<Value>`, тип которого определяется атрибутом `pw_type`. Ниже описаны все возможные структуры значений.

---

### Field.Dataset — поле из набора данных

Самый распространённый тип. Указывает на конкретное поле конкретного набора.

```xml
<Value pw_type="Field.Dataset"
       DatasetKey="d1e2f3a4-..."
       DatasetFieldKey="f1-..."
       DatasetFieldName="Номенклатура"
       IsRowField="true"
       IsQueryField="false"
       IsFunction="false">
  <!-- опционально: вложенный реквизит ссылочного поля -->
  <QueryField>Наименование</QueryField>
  <!-- опционально: функция над датой -->
  <FunctionName>BegOfMonth</FunctionName>
  <Datatypes>СправочникСсылка.Номенклатура</Datatypes>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `DatasetKey` | UUID набора данных |
| `DatasetFieldKey` | UUID поля внутри набора |
| `DatasetFieldName` | Имя поля (для читаемости) |
| `IsRowField` | `true` — поле принадлежит строке коллекции (`Collection`) |
| `IsQueryField` | `true` — поле является вложенным реквизитом ссылочного поля |
| `IsFunction` | `true` — к значению применяется функция даты |
| `AggregateFunction` | Агрегатная функция: `Sum`, `Count`, `CountDistinct`, `Max`, `Min`, `Avg`, `RunningTotal`, `PageTotal`, `PercentOfTotal`. `RunningTotal` / `PageTotal` / `PercentOfTotal` — построчные накопительные значения; `PageTotal` сбрасывается на каждой логической странице и доступен только для табличных макетов |
| `JoinKey` | UUID соединения (если поле из правого набора соединения) |
| `<QueryField>` | Имя вложенного реквизита (например `Наименование` у поля `Контрагент`) |
| `<FunctionName>` | Функция над датой — см. перечисление (см. topic: xml.Описание) |

---

### Field.Description — составное представление

Объединяет несколько полей в одну строку с префиксами и окончаниями. Используется когда в одной ячейке нужно вывести несколько реквизитов, например `ИНН: 7701234567, КПП: 770101001`.

```xml
<Value pw_type="Field.Description">
  <Row pw_type="Field.Description.Row" Number="1"
       Prefix="ИНН: " Ending=", ">
    <SourceField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="ИНН"/>
  </Row>
  <Row pw_type="Field.Description.Row" Number="2"
       Prefix="КПП: " Ending="">
    <SourceField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="КПП"/>
  </Row>
</Value>
```

Каждый элемент `Row` описывает одну часть составной строки:

| Атрибут / Элемент | Описание |
|---|---|
| `Number` | Порядковый номер части (1-based) |
| `Prefix` | Текст перед значением, например `"ИНН: "` |
| `Ending` | Текст после значения, например `", "` |
| `<SourceField>` | Источник значения — структура `Field.Dataset` |
| `<Format>` | Форматирование значения — структура `Format` |

---

### Field.SumInWords — сумма прописью

Выводит числовое значение прописью с указанием валюты. Например: `Пятнадцать тысяч рублей 00 копеек`.

```xml
<Value pw_type="Field.SumInWords">
  <NumberField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="СуммаДокумента"/>
  <CurrencyField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="Валюта"/>
  <CurrencyDefault>RUB</CurrencyDefault>
  <NoFractions>false</NoFractions>
  <FormatString/>
  <Parameters/>
</Value>
```

| Элемент | Описание |
|---|---|
| `<NumberField>` | Источник числового значения суммы — структура `Field.Dataset` |
| `<CurrencyField>` | Источник валюты — структура `Field.Dataset`. Если не указан, используется `CurrencyDefault` |
| `<CurrencyDefault>` | Валюта по умолчанию в ISO 4217: `RUB`, `USD`, `EUR`, `KZT` и др. |
| `<NoFractions>` | `true` — не выводить копейки / центы |
| `<FormatString>` | Строка форматирования (переопределяет стандартный вывод) |
| `<Parameters>` | Дополнительные параметры функции прописью |

---

### Field.QRCode — QR-код

Генерирует QR-код из данных. Поддерживает несколько форматов, включая УФЭБС для платёжных реквизитов.

```xml
<Value pw_type="Field.QRCode"
       Type="JSON"
       Accuracy="0"
       Size="200">
  <Algorithm/>
  <Rows>
    <Rows pw_type="Field.QRCode.Row" Name="ИНН">
      <SourceField pw_type="Field.Dataset"
                   DatasetKey="..." DatasetFieldKey="..."
                   DatasetFieldName="ИНН"/>
    </Rows>
    <Rows pw_type="Field.QRCode.Row" Name="Сумма">
      <SourceField pw_type="Field.Dataset"
                   DatasetKey="..." DatasetFieldKey="..."
                   DatasetFieldName="Сумма"/>
    </Rows>
  </Rows>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `Type` | Формат QR-кода — см. перечисление (см. topic: xml.Описание) |
| `Accuracy` | Уровень коррекции ошибок (0–3) |
| `Size` | Размер изображения в пикселях |
| `<Algorithm>` | Код на 1С для формирования данных (если `Type = Algorithm`) |
| `<Rows>` | Список полей для QR-кода (если `Type = Bank`, `XML` или `JSON`) |
| `Rows.Name` | Имя поля в структуре QR-кода |
| `Rows.<SourceField>` | Источник значения поля — структура `Field.Dataset` |
| `Rows.<Format>` | Форматирование значения перед кодированием |

---

### Field.Function — произвольный алгоритм

Вычисляемое значение — произвольный код на встроенном языке 1С. Результат функции подставляется в ячейку.

```xml
<Value pw_type="Field.Function">
  <Algorithm>
    Возврат Формат(ТекущаяДата(), "ДЛФ=D");
  </Algorithm>
</Value>
```

Внутри алгоритма доступны все данные макета: наборы, параметры, глобальные переменные формирования.

---

### Field.Attribute — дополнительное свойство (БСП)

Значение дополнительного реквизита или свойства объекта из подсистемы БСП («Свойства»).

```xml
<Value pw_type="Field.Attribute"
       AttrSetId="..."
       AttrSetName="НастройкиКонтрагентов"
       AttrId="..."
       AttrName="КатегорияКлиента"
       AttrDescription="Категория клиента">
  <AttrSetDescription>Настройки контрагентов</AttrSetDescription>
  <AttrIdDev>КатегорияКлиента</AttrIdDev>
  <SourceField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Контрагент"/>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `AttrSetId` / `AttrSetName` | Идентификатор и имя набора дополнительных реквизитов |
| `AttrId` / `AttrName` | Идентификатор и имя конкретного реквизита |
| `AttrDescription` | Представление реквизита для пользователя |
| `<SourceField>` | Поле-владелец реквизита (например, ссылка на контрагента) |

---

### Field.ContactInfo — контактная информация (БСП)

Значение контактной информации объекта из подсистемы БСП («Контактная информация»): телефон, адрес, email и т.п.

```xml
<Value pw_type="Field.ContactInfo"
       KindParentId="..."
       KindParentName="Контрагенты"
       KindId="..."
       KindName="ЮридическийАдрес"
       KindDescription="Юридический адрес">
  <KindIdDev>ЮридическийАдрес</KindIdDev>
  <KindNamePredefined/>
  <SourceField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Контрагент"/>
  <PeriodField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Дата"/>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `KindParentId` / `KindParentName` | Владелец вида контактной информации |
| `KindId` / `KindName` | Идентификатор и имя вида (например `ЮридическийАдрес`) |
| `KindDescription` | Представление для пользователя |
| `<SourceField>` | Поле-объект, для которого запрашивается контактная информация |
| `<PeriodField>` | Поле с датой актуальности (опционально) |

---

См. также: xml.Описание
