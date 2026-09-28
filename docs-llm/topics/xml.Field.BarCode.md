# Field.BarCode — штрихкод

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

Замечание: Доступно с версии 2026.3.24

Изображение штрихкода по значению из поля набора или результату алгоритма. Как это настраивается в конструкторе — глава Штрихкод (см. topic: штрихкод.Штрихкод).

```xml
<Value pw_type="Field.BarCode"
       Type="EAN13"
       Source="Dataset"
       Width="300"
       Height="100"
       ShowText="true"
       FontSize="12"
       RotationAngle="0"
       TransparentBackground="true"
       Scale="true"
       KeepProportions="false"
       VerticalAlign="1"
       GS1DatabarRowCount="2"
       RemoveExtraBackground="false"
       InputDataType="0"
       MonochromeFont="false">
  <Algorithm/>
  <SourceField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Штрихкод"/>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `Type` | Символика — см. перечисление (см. topic: xml.BarCode.Types) |
| `Source` | Источник значения — см. перечисление (см. topic: xml.BarCode.Sources) |
| `<Algorithm>` | Код на 1С, который возвращает значение (если `Source = Algorithm`); для поля набора — пустой |
| `<SourceField>` | Поле набора — структура `Field.Dataset` (если `Source = Dataset`) |
| `<Format>` | Форматирование значения — структура `Format`, необязательно. Применяется к значению, уже приведённому к строке, и только для `Source = Dataset` |
| `Width`, `Height` | Желаемый размер изображения в пикселях |
| `ShowText` | Выводить подпись со значением |
| `FontSize` | Размер шрифта подписи |
| `RotationAngle` | Угол поворота: `0`, `90`, `180`, `270` |
| `TransparentBackground` | Прозрачный фон |
| `Scale` | Масштабировать под заданный размер; меньше минимального размера символики изображение не будет |
| `KeepProportions` | Сохранять пропорции при масштабировании |
| `VerticalAlign` | Вертикальное выравнивание: `1` — по верхнему краю, `2` — по центру, `3` — по нижнему краю |
| `GS1DatabarRowCount` | Количество строк у символики `GS1DataBarExpandedStacked` |
| `RemoveExtraBackground` | Убирать пустые поля вокруг кода |
| `InputDataType` | Тип входных данных генератора. В конструкторе не показывается, при записи сохраняется как есть |
| `MonochromeFont` | Монохромный шрифт подписи. В конструкторе не показывается, при записи сохраняется как есть |

Файл, в котором есть `Field.BarCode`, читают версии 2026.3.24 и выше: более ранние версии отвергают его целиком, потому что не знают значения `BarCode` перечисления `Area.Parameter.Types`.

---

См. также: xml.ТипыЗначенийField, штрихкод.Штрихкод, xml.BarCode.Types, xml.BarCode.Sources
