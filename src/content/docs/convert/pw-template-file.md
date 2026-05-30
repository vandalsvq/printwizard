---
title: "pw#template#file"
sidebar:
  order: 2
  hidden: true
---

| Имя | Тип | Описание |
|--|--|--|
| version   | Строка | Номер версии сериализатора при выгрузке данных |
| data      | [pw#template#file#data](#pwtemplatefiledata) | Структура макета, с даннымы для экспорта |
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
| Описание              | [pw#template#about](/convert/pw-template/#pwtemplateabout) | Дополнительная информация о печатной форме |
| Метаданные            | [pw#template#metadata#row](/convert/pw-template/#pwtemplatemetadatarow) | Объекты метаданных, для которых создан макет |
| Запросы               | [pw#template#queries#row](/convert/pw-template/#pwtemplatequeriesrow) | Запросы к данным |
| ЗапросыПоля           | [pw#template#query#fields#row](/convert/pw-template/#pwtemplatequeryfieldsrow) | Поля запросов данных |
| Наборы                | [pw#template#datasets#row](/convert/pw-template/#pwtemplatedatasetsrow) | Наборы данных |
| НаборыПоля            | [pw#template#dataset#fields#row](/convert/pw-template/#pwtemplatedatasetfieldsrow) | Поля наборов данных |
| НаборыСоединения      | [pw#template#dataset#joins#row](/convert/pw-template/#pwtemplatedatasetjoinsrow) | Настройки соединения наборов |
| Области               | [pw#template#areas#row](/convert/pw-template/#pwtemplateareasrow) | Настройки областей макета печатной формы |
| ОбластиПараметры      | [pw#template#area#parameters#row](/convert/pw-template/#pwtemplateareaparametersrow) | Настройки параметров областей макета |
| ПараметрыЗапроса      | [pw#template#query#options#row](/convert/pw-template/#pwtemplatequeryoptionsrow) | Параметры для подстановки при выполнении запросов |
| ПараметрыПечати       | [pw#template#print#options#row](/convert/pw-template/#pwtemplateprintoptionsrow) | Параметры печати для табличного документа |
| Алгоритмы             | [pw#template#algorithms#row](/convert/pw-template/#pwtemplatealgorithmsrow) | Алгоритмы обработки событий макета |
| Функции               | [pw#template#functions#row](/convert/pw-template/#pwtemplatefunctionsrow) | Функции макета |
| ФункцииПараметры      | [pw#template#function#parameters#row](/convert/pw-template/#pwtemplatefunctionparametersrow) | Функции макета |
| Макет                 | Строка | Двоичные данные формата Base 16 (Hex) |

[в начало](#pwtemplatefile)
