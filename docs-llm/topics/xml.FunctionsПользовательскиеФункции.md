# Functions — пользовательские функции

Функции макета содержат повторно используемый код, доступный из алгоритмов и параметров областей.

```xml
<Functions pw_type="Function"
           Key="fn1-..."
           Name="ФорматДаты">
  <Description>Форматирует дату в строку вида «дд месяц гггг г.»</Description>
  <Algorithm>
    Дата = Параметры.Дата;
    Возврат Формат(Дата, "ДЛФ=D");
  </Algorithm>
  <Parameters>
    <Parameters pw_type="Function.Parameter"
                Number="1"
                Key="fnp1-..."
                Name="Дата">
      <Description>Дата для форматирования</Description>
      <Datatypes>Дата</Datatypes>
    </Parameters>
  </Parameters>
</Functions>
```

| Элемент / Атрибут | Описание |
|---|---|
| `<Description>` | Описание назначения функции |
| `<Algorithm>` | Тело функции на встроенном языке 1С |
| `<Parameters>` | Список параметров функции |
| `Parameters.Name` | Имя параметра — доступен внутри алгоритма как `Параметры.ИмяПараметра` |
| `Parameters.Number` | Порядковый номер параметра (1-based) |

---
