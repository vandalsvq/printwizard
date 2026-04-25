# Template

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
