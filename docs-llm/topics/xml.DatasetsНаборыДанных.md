# Datasets — наборы данных

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
| `Type` | Тип набора — см. перечисление (см. topic: xml.Описание) |
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

См. также: xml.Описание
