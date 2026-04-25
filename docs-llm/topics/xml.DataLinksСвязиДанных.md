# DataLinks — связи данных

Служебная коллекция, хранящая связи между элементами разных таблиц схемы. Используется для отслеживания зависимостей при редактировании схемы (каскадное обновление при переименовании набора, удалении поля и т.п.).

```xml
<DataLinks pw_type="DataLink" Key="dl1-...">
  <LeftTable>Datasets</LeftTable>
  <LeftKey>d1e2f3a4-...</LeftKey>
  <RightTable>Areas</RightTable>
  <RightKey>e1f2a3b4-...</RightKey>
  <Comment/>
</DataLinks>
```

| Элемент / Атрибут | Описание |
|---|---|
| `Key` | UUID записи связи |
| `<LeftTable>` | Имя таблицы источника: `Queries`, `Datasets`, `DatasetFields`, `Joins`, `Areas`, `AreaParameters` |
| `<LeftKey>` | UUID строки в таблице источника |
| `<RightTable>` | Имя таблицы цели |
| `<RightKey>` | UUID строки в таблице цели |
| `<Comment>` | Произвольный комментарий к связи |

---
