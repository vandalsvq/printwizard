# Template

Корневой элемент макета.

```xml
<Template pw_type="Template"
          Key="e7a1c3b2-..."
          Name="РеализацияТоваровУслуг">

  <Attributes IsRegistry="false"
              IsOfficeOpenXML="false"
              PrintParametersKey="ПараметрыПечати_СчётНаОплату">
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
| `PrintParametersKey` | | Пользовательский ключ параметров печати (`String(150)`). Используется как `ТабличныйДокумент.КлючПараметровПечати` при выводе. Если не задан — исполнитель формирует ключ из `Key` макета (`СтрЗаменить(Key, "-", "_")`). Позволяет сохранить пользовательские настройки полей, ориентации, масштаба между обновлениями макета и переиспользовать их между родственными макетами. |
| `<Presentation>` | ✅ | Краткое наименование (отображается в списке) |
| `<Description>` | | Полное наименование |
| `<Code>` | | Уникальный код макета |
| `<Comment>` | | Комментарий разработчика |

---
