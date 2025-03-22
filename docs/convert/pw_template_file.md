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
| data      | [pw#template#file#data][1] | Структура макета, с даннымы для экспорта |
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
| НаборыСоединения      | [pw#template#dataset#joins#row][27] | Настройки соединения наборов |
| Области               | [pw#template#areas#row][28] | Настройки областей макета печатной формы |
| ОбластиПараметры      | [pw#template#area#parameters#row][29] | Настройки параметров областей макета |
| ПараметрыЗапроса      | [pw#template#query#options#row][30] | Параметры для подстановки при выполнении запросов |
| ПараметрыПечати       | [pw#template#print#options#row][31] | Параметры печати для табличного документа |
| Алгоритмы             | [pw#template#algorithms#row][32] | Алгоритмы обработки событий макета |
| Функции               | [pw#template#functions#row][33] | Функции макета |
| ФункцииПараметры      | [pw#template#function#parameters#row][34] | Функции макета |
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
[27]: pw_template.html#pwtemplatedatasetjoinsrow
[28]: pw_template.html#pwtemplateareasrow
[29]: pw_template.html#pwtemplateareaparametersrow
[30]: pw_template.html#pwtemplatequeryoptionsrow
[31]: pw_template.html#pwtemplateprintoptionsrow
[32]: pw_template.html#pwtemplatealgorithmsrow
[33]: pw_template.html#pwtemplatefunctionsrow
[34]: pw_template.html#pwtemplatefunctionparametersrow