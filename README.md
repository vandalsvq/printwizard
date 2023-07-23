# PrintWizard (Мастер печатных форм)

[![Доработки](https://img.shields.io/github/issues/vandalsvq/printwizard/Доработки.svg?color=green&label=Доработки)](https://github.com/vandalsvq/printwizard/labels/%D0%94%D0%BE%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8)
[![Ошибки](https://img.shields.io/github/issues/vandalsvq/printwizard/Ошибки.svg?color=red&label=Ошибки)](https://github.com/vandalsvq/printwizard/labels/%D0%9E%D1%88%D0%B8%D0%B1%D0%BA%D0%B8)
[![Last release](https://img.shields.io/github/v/release/vandalsvq/printwizard?include_prereleases&label=Релиз&color=orange)](https://github.com/vandalsvq/printwizard/releases/latest)
[![Telegram](https://img.shields.io/badge/почитать-telegram-blue?style=flat&logo=telegram)](https://web.telegram.org/k/#-1692457352)

> * Расширение находится в процессе разработки
> * Community-версия планируется к выпуску в августе 2023
> * Коммерческая версия в сентябре 2023*. 
> * Для получения раннего доступа к community-версии, пишите мне в телеграм @vandalsvq

PrintWizard (мастер печатных форм, он же конструктор) - это расширение позволяющее абсолютно по-новому взглянуть на процесс разработки печатных форм. 

Зачем использовать конструктор:

* существенная экономия времени при разработке печатных форм
* создание и доработка печатной формы без конфигуратора
* стандартные кнопки "Печать" и дополнительные механизмы быстрой печати (по сочетанию Alt+P с анализом открытых форм)
* возможность экспорта во внешнюю печатную форму
* единообразие при проектировании печатных форм в формате табличного и офисного документа
* возможность разработки параллельно с существующей печатной формой

В дальнейших планах:

* поддержка групповой разработки с использованием хранилища или git
* выгрузка печатных форм в виде расширения с версионированием
* выгрузка расширения (внешней печатной формы) на сервере
* вывод в печатной форме штрих-кодов
* вывод в печатной форме картинок из базы данных
* поддержка форматированной строки (с версии 8.3.24)
* создание различных версий печатных форм на основании общего макета
* расширенные подсказки на основании методов конфигурации
* механизм универсальных алгоритмов (для использования в макетах)

Более подробно про [преимущества конструктора](#преимущества-конструктора) читайте ниже.

# Полезные ссылки

* [Документация](docs/README.md)
* [История версий](docs/history.md)
* [Скачать community-версию]() - в разработке
* [Публичные печатные формы](pdwx/README.md) - в разработке
* [Как сообщить об ошибке](docs/bug-report.md) - в разработке

# Преимущества конструктора

## Без конфигуратора

Печатные форму проектируются и дорабатываются в пользовательском режиме. 

Все интерфейсы конструктора построены таким образом, чтобы пользователю не потребовалось использовать конфигуратор. То есть от момента запроса к базе данных, до проектирования макета печатной формы и создания команды печати в форме пользовательского объекта.

Для удобства проектирования доступны такие инструменты как:

* конструктор запроса
* консоль кода с подсказками (на базе [bsl_console](https://github.com/salexdv/bsl_console))
* сравнение макетов печатных форм
* анализ наличия связи между полями данных и параметрами макета

В дальнейших планах:

* отладка макета (возможность посмотреть содержимое наборов на примере выбранных объектов данных)
* исследователь метаданных
* проверка при импорте ссылочных данных
* механизм рекомендаций (подсказка о ссылочных типах, доп. свойствах и реквизитах и т.п.)

## Прозрачность связей

Основная проблема "типичных" печатных форм, непрозрачность связи между макетом и источниками данных. Та самая ситуация, которая описывается как "смотришь в книгу, видишь фигу". Все видят текст, который выведен в печатную форму, но не каждый программист сразу найдет место в коде, где происходит присваиваение значения в параметр формы. А источник данных порой скрыт за цепочкой вызовов типовых методов.

В конструкторе, проследить связи не представляет никакой сложности. При этом пользователь может видеть как источник данных (запрос), так и алгоритмы или форматирование использованные при подготовке представления значения печатной формы.

## Нет привязки к конфигурации

Расширение может быть использовано практически в любой современной конфигурации, созданной на платформе 1С. Единственное требование, наличие БСП в основе конфигурации. При этом, конструктор не вносит изменения в конфигурацию, не требует снятия с поддержки и позволяет не переживать по поводу обновлений.

## Версионный контроль

Расширение позволяет создать собственную базу данных печатных форм. При этом каждый программист или бизнес-аналитик сможет увидеть как устроена печатная форма, при необходимости (и наличии прав) внести требуемые доработки.

В планах реализовать новые возможности для групповой разработки:

* хранение настроек печатных форм в git-репозиториях
* версионный контроль, с возможностью сравнения версий между собой

## Универсальность

Конструктор позволяет более универсально разрабатывать печатные формы:

* при проектировании доступны все объекты метаданных (конфигурации, расширений)
* доступны все созданные пользовательские данные (элементы справочник, документы и т.п., а не только предопределенные элементы)
* единоообразное формирование печатных форм в формате табличного и офисного документа (docx)
* возможность обмена настройками печатных форм

# Лицензирование

Существует две основных версии конструктора. Community-версия и коммерческая версия, подробнее отличия версий см. [тут](docs/community.md). Основное предназначение community-версии - популяризация конструктора и возможность ознакомления с функционалом конструктора. 

## Community-версия

С условиями использования вы можете ознакомится по данной [ссылке](docs/user_community.md).

Кратко, об особенностях данной версии:

* предназначеня для некоммерческого использования
* поставляется "как есть"
* содержит достаточно функционала для создания полноценных рабочих макетов
* печатные формы не отличаются от коммерческой версии

Важный момент: созданные макеты могут распространяться на коммерческой основе (в виде внешней обработки или файла *.pdwx). То есть, вы можете себе скачать и на копии локальной базы поставить данное расширение, создать макет и передать его заказчику. Предполагается, что заказчик уже имеет приобретенную коммерческую версию продукта. 

## Технические аспекты

* расширение имеет открытый исходный код
* расширение выполняет периодические обращения к интернет-сервисам, подробнее см. [тут](docs/internet-query.md)
  * на предмет наличия обновлений (в разработке)
  * на предмет наличия публичных печатных форм (в разработке)

# Компоненты

Для корректной работы расширения требуется:

* библиотека стандартных подсистем: 3.1.4 и выше ([список подсистем](docs/1c_ssl.md))
* платформа 1С:Предприятие: 8.3.18 и выше
* режим совместимости платформы: 8.3.14 и выше