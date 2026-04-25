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

---

См. также: xml.Описание
