# Field.QRCode — QR-код

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

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
| `Type` | Формат QR-кода — см. перечисление (см. topic: xml.QRCode.Type) |
| `Accuracy` | Уровень коррекции ошибок (0–3) |
| `Size` | Размер изображения в пикселях |
| `<Algorithm>` | Код на 1С для формирования данных (если `Type = Algorithm`) |
| `<Rows>` | Список полей для QR-кода (если `Type = Bank`, `XML` или `JSON`) |
| `Rows.Name` | Имя поля в структуре QR-кода |
| `Rows.<SourceField>` | Источник значения поля — структура `Field.Dataset` |
| `Rows.<Format>` | Форматирование значения перед кодированием |

---

См. также: xml.ТипыЗначенийField, xml.QRCode.Type
