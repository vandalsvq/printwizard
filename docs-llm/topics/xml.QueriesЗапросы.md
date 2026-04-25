# Queries — запросы

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
