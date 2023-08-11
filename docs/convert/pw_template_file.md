---
layout: default
title:  "pw#template#file"
parent: Сериализатор
nav_order: 2
---

<details open markdown="block">
  <summary>
    Содержание
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# pw#template#file

| Имя | Тип | Описание |
|--|--|--|
| version   | Строка | Номер версии сериализатора при выгрузке данных |
| data      | [pw#template#file#data][1] | Струткура макета, с даннымы для экспорта |
| metadata  | null | Не используется |
| type      | Строка | Всегда "pdw_data". Не используется, оставлено для совместимости с версией < 4.0> |

## pw#template#file#data

| Имя | Тип | Описание |
|--|--|--|
| Наименование          | Строка | Наименование печатной формы |
| Имя                   | Строка | Внутреннее имя печатной формы |
| ЭтоРеестр             | Булево | Признак формирования реестра (по всем ссылкам) |
| ЭтоOfficeOpenXML      | Булево | Признак печатной формы в формате *.docx |
| ВнешнийКлюч           | Строка | Уникальный ключ макета |
| ХешСумма              | Строка | Хеш сумма макета, используется для контроля наличия изменений |
| ОтметкаВремени        | Число | Отметка о времени последнего изменения |
| Описание              | [pw#template#about][21] | Дополнительная информация о печатной форме |
| Метаданные            | [pw#template#metadata#row][22] | Объекты метаданных, для которых создан макет |
| Запросы               | [pw#template#queries#row][23] | Запросы к данным |
| ЗапросыПоля           | [pw#template#query#fields#row][24] | Поля запросов данных |
| Наборы                | [pw#template#datasets#row][25] | Наборы данных |
| НаборыПоля            | [pw#template#dataset#fields#row][26] | Поля наборов данных |
| НаборыПредставления   | [pw#template#dataset#wizards#row][27] | Настройки формирования ПолеКонструктора |
| НаборыНумераторы      | [pw#template#dataset#numerators#row][28] | Настройки формирования ПолеНумератора |
| НаборыСоединения      | [pw#template#dataset#joins#row][29] | Настройки соединения наборов |
| Области               | [pw#template#areas#row][30] | Настройки областей макета печатной формы |
| ОбластиПараметры      | [pw#template#area#parameters#row][31] | Настройки параметров областей макета |
| ОбластиПредставления  | [pw#template#area#wizards#row][32] | Настройки формирования ПолеКонструктора параметра области |
| ПараметрыЗапроса      | [pw#template#query#options#row][33] | Параметры для подстановки при выполнении запросов |
| ПараметрыПечати       | [pw#template#print#options#row][34] | Параметры печати для табличного документа |
| Алгоритмы             | [pw#template#algorithms#row][35] | Алгоритмы обработки событий макета |
| Макет                 | Строка | Двоичные данные формата Base 16 (Hex) |

[в начало][0]


[0]: #pwtemplatefile
[1]: #pwtemplatefiledata

[21]: pw_template.html#pwtemplateabout
[22]: pw_template.html#pwtemplatemetadatarow
[23]: pw_template.html#pwtemplatequeriesrow
[24]: pw_template.html#pwtemplatequeryfieldsrow
[25]: pw_template.html#pwtemplatedatasetsrow
[26]: pw_template.html#pwtemplatedatasetfieldsrow
[27]: pw_template.html#pwtemplatedatasetwizardsrow
[28]: pw_template.html#pwtemplatedatasetnumeratorsrow
[29]: pw_template.html#pwtemplatedatasetjoinsrow
[30]: pw_template.html#pwtemplateareasrow
[31]: pw_template.html#pwtemplateareaparametersrow
[32]: pw_template.html#pwtemplateareawizardsrow
[33]: pw_template.html#pwtemplatequeryoptionsrow
[34]: pw_template.html#pwtemplateprintoptionsrow
[35]: pw_template.html#pwtemplatealgorithmsrow