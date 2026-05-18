# Areas — области шаблона

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

| Атрибут / Элемент | Описание |
|---|---|
| `PrintMethod` | Способ вывода — см. перечисление (см. topic: xml.Описание) |
| `PrintSettings` | Дополнительная настройка — см. перечисление (см. topic: xml.Описание) |
| `DatasetKey` | Ключ связанного набора данных (обязателен для `Collection`) |
| `Order` | Порядок вывода области |
| `<WrapParameter>` | Имя параметра-признака переноса (для `PrintMethod = Wrap`) |
| `<WrapAddAreaName>` | Имя дополнительной области переноса |
| `<WrapControlAreaName1>` | Имя первой контрольной области переноса |
| `<WrapControlAreaName2>` | Имя второй контрольной области переноса |

### Area.Parameter — типы привязки ячейки

| Значение `Type` | Описание | Тип значения `<Value>` |
|---|---|---|
| `Dataset` | Поле из набора данных | `Field.Dataset` |
| `Description` | Составное представление | `Field.Description` |
| `Algorithm` | Произвольный код 1С | `Field.Function` |
| `SumInWords` | Сумма прописью | `Field.SumInWords` |
| `QRCode` | QR-код | `Field.QRCode` |

### Area.OutputRule — условие вывода области

Декларативное условие вывода области без использования события `BeforeAreaOutput`. Если на области заданы правила вывода — исполнитель **до** вызова `BeforeAreaOutput` вычисляет все включённые правила, объединяет результаты по логическому `И` и при `Ложь` пропускает вывод области (соседние области и повторения выводятся в штатном порядке).

```xml
<Areas pw_type="Area" ...>
  <Parameters> ... </Parameters>

  <OutputRules pw_type="Area.OutputRule"
               Key="r1-..."
               Order="1"
               Use="true"
               ComparisonType="NotEqual">
    <LeftValue pw_type="Field.Dataset"
               DatasetKey="..."
               DatasetFieldKey="..."
               DatasetFieldName="Контрагент.ЭтоФизическоеЛицо"/>
    <RightValue xsi:type="xs:boolean">true</RightValue>
  </OutputRules>
</Areas>
```

| Атрибут / Элемент | Описание |
|---|---|
| `Key` | Уникальный ключ правила (GUID) |
| `UserID` | Пользовательский идентификатор (опционально) |
| `Order` | Порядок применения правил в пределах области |
| `Use` | Использование правила; `false` — правило игнорируется |
| `ComparisonType` | Вид сравнения — см. перечисление (см. topic: xml.Описание) |
| `<LeftValue>` | Левое значение — всегда `Field.Dataset` (поле набора данных) |
| `<RightValue>` | Правое значение — произвольное значение, тип определяется через `xsi:type` |

Свойство `OutputRules` на `Area` опционально (`minOccurs=0`). Существующие схемы без блока `OutputRules` остаются полностью совместимыми с версией 6.1.

**Семантика исполнения:**

- Правила с `Use = false` пропускаются.
- Для каждого включённого правила вычисляется фактическое значение поля по `LeftValue`, десериализуется `RightValue`, применяется `ComparisonType`.
- Итог — логическое `И` всех правил. Пустой список включённых правил даёт `true`.
- При ошибке вычисления / десериализации правило трактуется как `false` (с записью в журнал регистрации исполнителем).

---

См. также: xml.Описание
