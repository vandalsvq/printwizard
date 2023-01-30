# ver-1.0.7.3, 30.01.2023

* продолжение развития механизма сравнения макетов
* унифицирован код вызова консоли кода, добавлена форма сравнения кода
* исправление ошибок:
  * [#10](https://github.com/vandalsvq/printwizard/issues/10);
  * [#15](https://github.com/vandalsvq/printwizard/issues/15);
  * [#16](https://github.com/vandalsvq/printwizard/issues/16);
  * [#17](https://github.com/vandalsvq/printwizard/issues/17)

# ver-1.0.7.2, Январь 2023

- Исправлены ошибки:
  - [#4](https://github.com/vandalsvq/printwizard/issues/4)
  - [#5](https://github.com/vandalsvq/printwizard/issues/5)
  - [#6](https://github.com/vandalsvq/printwizard/issues/6)

# ver-1.0.7.1, Январь 2023

- Добавлен механизм проверки связи полей наборов данных с различными элементами макета (другие поля, области, параметры и пр.) ([#3](https://github.com/vandalsvq/printwizard/issues/3))
- Справочник "Макеты"
  - Добавлены реквизиты ХешСумма, ОтметкаВремени - изменяются при записи макета, если данные были изменены
  - Тест печати в форме макета реализован через штатный механизм БСП
- Добавлен прототип механизма сравнения макетов
- Добавлен универсальный сериализатор данных макета (используется для экспорта, печати и внутренних нужд)
- Доработан формат выгрузки макета в файл (pdwx). Новая версия 4.0. Отказ от поддержки версий ниже 3.0
- Исправлены ошибки:
  - [#1](https://github.com/vandalsvq/printwizard/issues/1)
  - [#2](https://github.com/vandalsvq/printwizard/issues/2)


