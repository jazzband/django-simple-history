# Changelog

## [Unreleased](https://github.com/jazzband/django-simple-history/tree/HEAD)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/3.0.0...HEAD)

**Closed issues:**

- test\_sameinstant is not idempotent [\#861](https://github.com/jazzband/django-simple-history/issues/861)
- Pull request checklist requires "make format" however "make init" does not prepare for it [\#859](https://github.com/jazzband/django-simple-history/issues/859)
- Cannot resolve keyword 'history' into field.  [\#833](https://github.com/jazzband/django-simple-history/issues/833)
- djangorestframework 3.12.3 introduced bug where HistoricalModel cannot be used with OrderingFilter [\#821](https://github.com/jazzband/django-simple-history/issues/821)

**Merged pull requests:**

- Remove previous code of conduct. [\#874](https://github.com/jazzband/django-simple-history/pull/874) ([tim-schilling](https://github.com/tim-schilling))
- Ensure that latest\(\) is idempotent. [\#862](https://github.com/jazzband/django-simple-history/pull/862) ([jeking3](https://github.com/jeking3))
- Change `make docs` and `make format` to use tox so they succeed. [\#860](https://github.com/jazzband/django-simple-history/pull/860) ([jeking3](https://github.com/jeking3))
- Typo: Remove double "the" from documentation [\#854](https://github.com/jazzband/django-simple-history/pull/854) ([christianhpoe](https://github.com/christianhpoe))
- Fix documentation display issue [\#835](https://github.com/jazzband/django-simple-history/pull/835) ([dracos](https://github.com/dracos))
- Fix bug where descriptor class missed instance=None case [\#822](https://github.com/jazzband/django-simple-history/pull/822) ([hwalinga](https://github.com/hwalinga))

## [3.0.0](https://github.com/jazzband/django-simple-history/tree/3.0.0) (2021-04-16)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.12.0...3.0.0)

**Closed issues:**

- Django 3.2 please bump release to support it \(TextFields db\_collation\) [\#813](https://github.com/jazzband/django-simple-history/issues/813)
- Update test matrix for Django Dev [\#799](https://github.com/jazzband/django-simple-history/issues/799)
- How to access the history model in models.py if simple\_history.register\(\) is used. [\#781](https://github.com/jazzband/django-simple-history/issues/781)
- The changes field records all the data [\#760](https://github.com/jazzband/django-simple-history/issues/760)
- Sort imports with isort [\#751](https://github.com/jazzband/django-simple-history/issues/751)
- Use asgiref when available instead of thread locals [\#747](https://github.com/jazzband/django-simple-history/issues/747)
- Add Python 3.9 support [\#745](https://github.com/jazzband/django-simple-history/issues/745)
- Enable dependabot [\#741](https://github.com/jazzband/django-simple-history/issues/741)
- Would you \*\*please\*\* add m2m support? [\#740](https://github.com/jazzband/django-simple-history/issues/740)
- Migrate from TravisCI to Github Actions [\#739](https://github.com/jazzband/django-simple-history/issues/739)
- Support ignore\_conflicts parameter in bulk\_create\_with\_history [\#732](https://github.com/jazzband/django-simple-history/issues/732)
- How would I add an update record without making any changes to the object. [\#731](https://github.com/jazzband/django-simple-history/issues/731)
- How would I add an update record without making any changes to the object. [\#730](https://github.com/jazzband/django-simple-history/issues/730)
- Django 3.1 support - request.user now django.utils.functional.SimpleLazyObject [\#728](https://github.com/jazzband/django-simple-history/issues/728)
- History Diffing for Fields With Foreign Keys Returns Primary Key Values And Not The Name of the Field. [\#725](https://github.com/jazzband/django-simple-history/issues/725)
- Querying history on a related model with as\_of [\#715](https://github.com/jazzband/django-simple-history/issues/715)
- How to save change reason on model row delete [\#712](https://github.com/jazzband/django-simple-history/issues/712)
- Tracking model history with foreign key points to the latest object only [\#711](https://github.com/jazzband/django-simple-history/issues/711)
- Add new version/record without updating main model [\#705](https://github.com/jazzband/django-simple-history/issues/705)
- raise PermissionDenied in history\_view [\#704](https://github.com/jazzband/django-simple-history/issues/704)
- IntegrityError FOREIGN KEY constraint failed [\#697](https://github.com/jazzband/django-simple-history/issues/697)
- Question: ForeignKey/ManyToMany support [\#690](https://github.com/jazzband/django-simple-history/issues/690)
- Implement Jazzband guidelines for django-simple-history [\#670](https://github.com/jazzband/django-simple-history/issues/670)
- Remove support for Django 1.11, 2.0, and 2.1 [\#652](https://github.com/jazzband/django-simple-history/issues/652)
- Add support for testing against multiple DBs [\#445](https://github.com/jazzband/django-simple-history/issues/445)

**Merged pull requests:**

- fix title underline [\#820](https://github.com/jazzband/django-simple-history/pull/820) ([barm](https://github.com/barm))
- Remove changeReason and update CHANGES to prepare for 3.0.0 [\#819](https://github.com/jazzband/django-simple-history/pull/819) ([barm](https://github.com/barm))
- Update django support [\#817](https://github.com/jazzband/django-simple-history/pull/817) ([hramezani](https://github.com/hramezani))
- Improve French translations [\#811](https://github.com/jazzband/django-simple-history/pull/811) ([LeMinaw](https://github.com/LeMinaw))
- Rename Django's dev branch to main. [\#807](https://github.com/jazzband/django-simple-history/pull/807) ([jezdez](https://github.com/jezdez))
- Updated test matrix -- Django Dev dropped support for Python3.6 and 3.7 [\#800](https://github.com/jazzband/django-simple-history/pull/800) ([smithdc1](https://github.com/smithdc1))
- Add DEFAULT\_AUTO\_FIELD to test settings. [\#774](https://github.com/jazzband/django-simple-history/pull/774) ([hramezani](https://github.com/hramezani))
- Make tests pass after 2021/01/01 [\#772](https://github.com/jazzband/django-simple-history/pull/772) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Update GitHub Actions migration to match other Jazzband projects. [\#769](https://github.com/jazzband/django-simple-history/pull/769) ([jezdez](https://github.com/jezdez))
- Queryset history "as\_of" speed improvements [\#759](https://github.com/jazzband/django-simple-history/pull/759) ([TyrantWave](https://github.com/TyrantWave))
- MySQL support [\#755](https://github.com/jazzband/django-simple-history/pull/755) ([rossmechanic](https://github.com/rossmechanic))
- Use codecov in informational mode to ignore its build status [\#754](https://github.com/jazzband/django-simple-history/pull/754) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Add postgres to testing matrix [\#753](https://github.com/jazzband/django-simple-history/pull/753) ([rossmechanic](https://github.com/rossmechanic))
- Sort imports with isort [\#752](https://github.com/jazzband/django-simple-history/pull/752) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Fix logging error output [\#750](https://github.com/jazzband/django-simple-history/pull/750) ([rossmechanic](https://github.com/rossmechanic))
- Use asgiref when available instead of thread locals [\#749](https://github.com/jazzband/django-simple-history/pull/749) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Enforce py35 support when formatting with black [\#748](https://github.com/jazzband/django-simple-history/pull/748) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Autoformat python files under docs directory [\#746](https://github.com/jazzband/django-simple-history/pull/746) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Add Python 3.9 support [\#744](https://github.com/jazzband/django-simple-history/pull/744) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Enable dependabot [\#742](https://github.com/jazzband/django-simple-history/pull/742) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Migrate from TravisCI to Github Actions [\#738](https://github.com/jazzband/django-simple-history/pull/738) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Removed mock dependency [\#737](https://github.com/jazzband/django-simple-history/pull/737) ([smithdc1](https://github.com/smithdc1))
- fix: do not load historic in memory in clean\_old\_history command [\#735](https://github.com/jazzband/django-simple-history/pull/735) ([vied12](https://github.com/vied12))
- Updated back version to 20.8.b1 [\#734](https://github.com/jazzband/django-simple-history/pull/734) ([smithdc1](https://github.com/smithdc1))
- Add ignore\_conflicts to bulk\_create\_with\_history [\#733](https://github.com/jazzband/django-simple-history/pull/733) ([shihanng](https://github.com/shihanng))
- Add release config. [\#727](https://github.com/jazzband/django-simple-history/pull/727) ([jezdez](https://github.com/jezdez))
- Removed support for django versions prior to 2.2 [\#719](https://github.com/jazzband/django-simple-history/pull/719) ([smithdc1](https://github.com/smithdc1))

## [2.12.0](https://github.com/jazzband/django-simple-history/tree/2.12.0) (2020-10-14)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.11.0...2.12.0)

**Fixed bugs:**

- IntegrityError when deleting user [\#391](https://github.com/jazzband/django-simple-history/issues/391)

**Closed issues:**

- providing\_args deprecation warning Django 3.1 [\#723](https://github.com/jazzband/django-simple-history/issues/723)
- clean\_old\_history days arg does not accept value [\#721](https://github.com/jazzband/django-simple-history/issues/721)
- Add support for Django 3.1 [\#714](https://github.com/jazzband/django-simple-history/issues/714)
- `as_of` fails on a model with an excluded ManyToManyField [\#706](https://github.com/jazzband/django-simple-history/issues/706)
- `bulk_update_with_history` to support alternative model managers [\#703](https://github.com/jazzband/django-simple-history/issues/703)
- Summary of Recent Changes [\#701](https://github.com/jazzband/django-simple-history/issues/701)
- Feature: Direct access to related model history from history object [\#700](https://github.com/jazzband/django-simple-history/issues/700)
- bulk\_create\_with\_history fails if the model has a ManyToManyField [\#698](https://github.com/jazzband/django-simple-history/issues/698)
- Delete a column, the operation record\(+,-,~\) related to this column has not been deleted [\#696](https://github.com/jazzband/django-simple-history/issues/696)
- Restore a column deleted by mistake through django-simple-history [\#695](https://github.com/jazzband/django-simple-history/issues/695)
- How to revert deleted objects in django admin? [\#693](https://github.com/jazzband/django-simple-history/issues/693)
- how to Save initial object content in history only when object is updated or deleted? [\#692](https://github.com/jazzband/django-simple-history/issues/692)
- Clashes with reverse query name \(related\_query\_name in Models\) [\#691](https://github.com/jazzband/django-simple-history/issues/691)
- Add option to set the default date when bulk creating or updating [\#686](https://github.com/jazzband/django-simple-history/issues/686)
- Wrong link to docs in "About" \(of this github project\) [\#685](https://github.com/jazzband/django-simple-history/issues/685)
- Can you get a User's history? [\#684](https://github.com/jazzband/django-simple-history/issues/684)
- django admin site changes doesn't save in history form  [\#683](https://github.com/jazzband/django-simple-history/issues/683)
- About related objects \(onetoone, foreignkey, manytomany\) [\#682](https://github.com/jazzband/django-simple-history/issues/682)
- Add history\_changed\_fields field  [\#681](https://github.com/jazzband/django-simple-history/issues/681)
- clear\_duplicate\_history command feature: allow to exclude some fields from `diff_against` check [\#674](https://github.com/jazzband/django-simple-history/issues/674)
- Admin view needs `has_view_permission` in context for Django 2.1 [\#443](https://github.com/jazzband/django-simple-history/issues/443)

**Merged pull requests:**

- Prepare for v2.12.0 release! [\#724](https://github.com/jazzband/django-simple-history/pull/724) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- fix: clean\_old\_history's days argument acccepts integer [\#722](https://github.com/jazzband/django-simple-history/pull/722) ([vied12](https://github.com/vied12))
- Added SECRET\_KEY to DEFAULT\_SETTINGS [\#718](https://github.com/jazzband/django-simple-history/pull/718) ([smithdc1](https://github.com/smithdc1))
- Add support for Django 3.1 [\#713](https://github.com/jazzband/django-simple-history/pull/713) ([martinfrancois](https://github.com/martinfrancois))
- Override "submit\_buttons\_top" section to prevent KeyError in context [\#710](https://github.com/jazzband/django-simple-history/pull/710) ([john-parton](https://github.com/john-parton))
- Bulk create and update support for alternative managers [\#709](https://github.com/jazzband/django-simple-history/pull/709) ([georgek](https://github.com/georgek))
- Exclude ManyToManyFields when fetching excluded fields. [\#707](https://github.com/jazzband/django-simple-history/pull/707) ([j-wing](https://github.com/j-wing))
- Patches for Django warnings [\#702](https://github.com/jazzband/django-simple-history/pull/702) ([atodorov](https://github.com/atodorov))
- Exclude ManyToManyFields when using bulk\_create\_with\_history [\#699](https://github.com/jazzband/django-simple-history/pull/699) ([sbuss](https://github.com/sbuss))
- Method import name typo fix [\#694](https://github.com/jazzband/django-simple-history/pull/694) ([marablayev](https://github.com/marablayev))
- feat: add default\_date optional parameter for bulk create and update [\#687](https://github.com/jazzband/django-simple-history/pull/687) ([sbor23](https://github.com/sbor23))
- Allow to exclude some fields from `diff_against` check [\#680](https://github.com/jazzband/django-simple-history/pull/680) ([MaximZemskov](https://github.com/MaximZemskov))

## [2.11.0](https://github.com/jazzband/django-simple-history/tree/2.11.0) (2020-06-20)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.10.0...2.11.0)

**Closed issues:**

- Is there a way to enable history on some models [\#665](https://github.com/jazzband/django-simple-history/issues/665)
- no name module [\#662](https://github.com/jazzband/django-simple-history/issues/662)
- Is there a script to import old admin history? [\#661](https://github.com/jazzband/django-simple-history/issues/661)
- \_change\_reason on model instance does not set history\_change\_reason on save [\#660](https://github.com/jazzband/django-simple-history/issues/660)
- How to display additional field in historical admin form? [\#659](https://github.com/jazzband/django-simple-history/issues/659)
- Add possibility to specify a default user for bulk\_create\_with\_history [\#635](https://github.com/jazzband/django-simple-history/issues/635)
- Ability to disable admin Revert functionality [\#602](https://github.com/jazzband/django-simple-history/issues/602)
- Add support of bulk\_create\_with\_history for databases others to PostgreSQL [\#577](https://github.com/jazzband/django-simple-history/issues/577)
- Adopt conflict-resistant changelog generator [\#456](https://github.com/jazzband/django-simple-history/issues/456)
- Create alias for camel cased `changeReason` [\#455](https://github.com/jazzband/django-simple-history/issues/455)

**Merged pull requests:**

- Bump version to 2.11.0 [\#679](https://github.com/jazzband/django-simple-history/pull/679) ([rossmechanic](https://github.com/rossmechanic))
- Get default user for bulk ops from middleware [\#677](https://github.com/jazzband/django-simple-history/pull/677) ([rossmechanic](https://github.com/rossmechanic))
- Remove db constraint on historical user to prevent IntegrityError  [\#676](https://github.com/jazzband/django-simple-history/pull/676) ([keithhackbarth](https://github.com/keithhackbarth))
- Added a Clean old history command to clean older history entries by cron/task [\#675](https://github.com/jazzband/django-simple-history/pull/675) ([PauloPeres](https://github.com/PauloPeres))
- Implement Jazzband guidelines [\#671](https://github.com/jazzband/django-simple-history/pull/671) ([treyhunner](https://github.com/treyhunner))
- synchronize version table of index.rst with readme.rst [\#669](https://github.com/jazzband/django-simple-history/pull/669) ([Kyutatsu](https://github.com/Kyutatsu))
- Remove invalid reference in docs [\#667](https://github.com/jazzband/django-simple-history/pull/667) ([jws](https://github.com/jws))
- Fix formatting in doc [\#658](https://github.com/jazzband/django-simple-history/pull/658) ([johnthagen](https://github.com/johnthagen))

## [2.10.0](https://github.com/jazzband/django-simple-history/tree/2.10.0) (2020-04-27)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.9.0...2.10.0)

**Closed issues:**

- Bulk update with history [\#649](https://github.com/jazzband/django-simple-history/issues/649)
- bulk\_update\_with\_history [\#528](https://github.com/jazzband/django-simple-history/issues/528)

**Merged pull requests:**

- fix formatting on changes file [\#657](https://github.com/jazzband/django-simple-history/pull/657) ([rossmechanic](https://github.com/rossmechanic))
- Bump version 2.10.0 [\#656](https://github.com/jazzband/django-simple-history/pull/656) ([rossmechanic](https://github.com/rossmechanic))
- Deprecate changereason [\#655](https://github.com/jazzband/django-simple-history/pull/655) ([rossmechanic](https://github.com/rossmechanic))
- French translation [\#654](https://github.com/jazzband/django-simple-history/pull/654) ([delahondes](https://github.com/delahondes))
- Add default\_user or default\_change\_reason for bulk\_create or bulk\_update [\#653](https://github.com/jazzband/django-simple-history/pull/653) ([rossmechanic](https://github.com/rossmechanic))
- Update AUTHORS.rst [\#651](https://github.com/jazzband/django-simple-history/pull/651) ([jihoon796](https://github.com/jihoon796))
- Add bulk\_update\_with\_history  [\#650](https://github.com/jazzband/django-simple-history/pull/650) ([jihoon796](https://github.com/jihoon796))

## [2.9.0](https://github.com/jazzband/django-simple-history/tree/2.9.0) (2020-04-23)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.8.0...2.9.0)

**Closed issues:**

- Update the doc, please [\#645](https://github.com/jazzband/django-simple-history/issues/645)
- Readonly fields with `SIMPLE_HISTORY_EDIT=False` [\#640](https://github.com/jazzband/django-simple-history/issues/640)
- Assigning User object to changed\_by attribute gives Error [\#639](https://github.com/jazzband/django-simple-history/issues/639)
- It Recorded without changing fields [\#638](https://github.com/jazzband/django-simple-history/issues/638)
- Documentation is out of date [\#633](https://github.com/jazzband/django-simple-history/issues/633)
- Load ContentType model using django\_apps instead of direct import [\#629](https://github.com/jazzband/django-simple-history/issues/629)
- excluded\_fields doesn't work on register\(User\) in Django [\#628](https://github.com/jazzband/django-simple-history/issues/628)
- rate limit history of models? [\#626](https://github.com/jazzband/django-simple-history/issues/626)
- no such table: auth\_historicaluser when running Bitbucket Pipeline [\#624](https://github.com/jazzband/django-simple-history/issues/624)
- FileField should be transformed into a CharField instead of a TextField [\#623](https://github.com/jazzband/django-simple-history/issues/623)
- Migrations break for ManyToMany models [\#622](https://github.com/jazzband/django-simple-history/issues/622)
- Is it possible to show the changed field/fields on the Change history table? [\#621](https://github.com/jazzband/django-simple-history/issues/621)
- How to prevent a requested change from being recorded? [\#619](https://github.com/jazzband/django-simple-history/issues/619)
- Model.validate\_unique incompatible with django-simple-history [\#618](https://github.com/jazzband/django-simple-history/issues/618)
- Can't recreate historical instance when using Inheritance [\#615](https://github.com/jazzband/django-simple-history/issues/615)
- Documentation - requests for clarification [\#612](https://github.com/jazzband/django-simple-history/issues/612)
- "minutes" flag still checks historical records for records that have never changed [\#605](https://github.com/jazzband/django-simple-history/issues/605)
- Better documentation for multiple databases [\#581](https://github.com/jazzband/django-simple-history/issues/581)

**Merged pull requests:**

- Revert GH-641 [\#648](https://github.com/jazzband/django-simple-history/pull/648) ([rossmechanic](https://github.com/rossmechanic))
- Fix doc error [\#647](https://github.com/jazzband/django-simple-history/pull/647) ([rossmechanic](https://github.com/rossmechanic))
- Bump version to 2.9.0 [\#646](https://github.com/jazzband/django-simple-history/pull/646) ([rossmechanic](https://github.com/rossmechanic))
- Added how to prefetch\_related to documentation [\#644](https://github.com/jazzband/django-simple-history/pull/644) ([mahsa-lotfi92](https://github.com/mahsa-lotfi92))
- Changed timezone.now import to `from django.utils import timezone` [\#643](https://github.com/jazzband/django-simple-history/pull/643) ([sevetseh28](https://github.com/sevetseh28))
- Make history fields readonly when `SIMPLE_HISTORY_EDIT` is not set or set to `False` [\#641](https://github.com/jazzband/django-simple-history/pull/641) ([partizaans](https://github.com/partizaans))
- Hotfix/update change reason with excluded fields [\#637](https://github.com/jazzband/django-simple-history/pull/637) ([alpha1d3d](https://github.com/alpha1d3d))
- synchronize version table with readme.rst [\#634](https://github.com/jazzband/django-simple-history/pull/634) ([hellerbarde](https://github.com/hellerbarde))
- Enable/ disable revert using only a settings attribute [\#632](https://github.com/jazzband/django-simple-history/pull/632) ([erikvw](https://github.com/erikvw))
- import ContentType via property / django\_apps.get\_model [\#630](https://github.com/jazzband/django-simple-history/pull/630) ([erikvw](https://github.com/erikvw))
- Adding notes on BitBucket Pipelines [\#627](https://github.com/jazzband/django-simple-history/pull/627) ([StevenMapes](https://github.com/StevenMapes))
- Add setting to convert FileField to CharField instead of TextField [\#625](https://github.com/jazzband/django-simple-history/pull/625) ([jcushman](https://github.com/jcushman))
- Added django 3.0 to test matrix [\#613](https://github.com/jazzband/django-simple-history/pull/613) ([rossmechanic](https://github.com/rossmechanic))
- Filter the records when given a minutes argument [\#606](https://github.com/jazzband/django-simple-history/pull/606) ([craigmaloney](https://github.com/craigmaloney))

## [2.8.0](https://github.com/jazzband/django-simple-history/tree/2.8.0) (2019-12-02)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.7.3...2.8.0)

**Closed issues:**

- Pin `black` to a specific version, so that new PRs don't fail the build extraneously [\#608](https://github.com/jazzband/django-simple-history/issues/608)
- Add tests for \#585 [\#607](https://github.com/jazzband/django-simple-history/issues/607)
- OOM when using clean\_duplicate\_history on over 8M records [\#603](https://github.com/jazzband/django-simple-history/issues/603)
- 'Options' object has no attribute 'simple\_history\_manager\_attribute' [\#600](https://github.com/jazzband/django-simple-history/issues/600)
- Django 3 support [\#598](https://github.com/jazzband/django-simple-history/issues/598)
- Missing closing parenthesis in documentation example [\#596](https://github.com/jazzband/django-simple-history/issues/596)
- Read the Docs Django version support 2.2 missing [\#595](https://github.com/jazzband/django-simple-history/issues/595)
- SQL error at bulk\_create\_with\_history [\#592](https://github.com/jazzband/django-simple-history/issues/592)
- create\_historical\_record on demand [\#591](https://github.com/jazzband/django-simple-history/issues/591)
- History Diffing - Display the \_\_str\_\_ value instead of the id for foreign key fields [\#587](https://github.com/jazzband/django-simple-history/issues/587)
- makemigrations error [\#584](https://github.com/jazzband/django-simple-history/issues/584)
- history\_user\_id\_field not supported with Django 1.11 [\#583](https://github.com/jazzband/django-simple-history/issues/583)
- diff\_against doesn't detect changes to parent model attributes when using inherited models [\#575](https://github.com/jazzband/django-simple-history/issues/575)
- Historical model with "excluded\_fields" causes DoesNotExist error when trying to get instance from historical record if object is deleted [\#571](https://github.com/jazzband/django-simple-history/issues/571)

**Merged pull requests:**

- Bump version to 2.8.0 [\#611](https://github.com/jazzband/django-simple-history/pull/611) ([rossmechanic](https://github.com/rossmechanic))
- Added Django 3 and Python 3.8 support [\#610](https://github.com/jazzband/django-simple-history/pull/610) ([rossmechanic](https://github.com/rossmechanic))
- Pin black to specific version [\#609](https://github.com/jazzband/django-simple-history/pull/609) ([rossmechanic](https://github.com/rossmechanic))
- Add an iterator to prevent OOM when cleaning large databases [\#604](https://github.com/jazzband/django-simple-history/pull/604) ([craigmaloney](https://github.com/craigmaloney))
- Add missing parenthesis to example [\#597](https://github.com/jazzband/django-simple-history/pull/597) ([guilleijo](https://github.com/guilleijo))
- Fixed bulk\_create\_with\_history support for relation\_name attribute [\#593](https://github.com/jazzband/django-simple-history/pull/593) ([xahgmah](https://github.com/xahgmah))
- Update outdated admin screenshots [\#590](https://github.com/jazzband/django-simple-history/pull/590) ([rossmechanic](https://github.com/rossmechanic))
- Add black reformatting to all files [\#589](https://github.com/jazzband/django-simple-history/pull/589) ([rossmechanic](https://github.com/rossmechanic))
- django 2.2 added to supported versions [\#586](https://github.com/jazzband/django-simple-history/pull/586) ([hhuseyinpay](https://github.com/hhuseyinpay))
- Instantiate model with kwargs not args to allow for excluded fields [\#585](https://github.com/jazzband/django-simple-history/pull/585) ([PeteCoward](https://github.com/PeteCoward))
- Update common\_issues.rst [\#580](https://github.com/jazzband/django-simple-history/pull/580) ([majdal](https://github.com/majdal))
- Update common\_issues.rst [\#579](https://github.com/jazzband/django-simple-history/pull/579) ([majdal](https://github.com/majdal))
- Make bulk\_create\_with\_history working not only with PostgreSQL [\#578](https://github.com/jazzband/django-simple-history/pull/578) ([xahgmah](https://github.com/xahgmah))
- fix \#575 use django model\_to\_dict to detect changes in parent models [\#576](https://github.com/jazzband/django-simple-history/pull/576) ([marcanuy](https://github.com/marcanuy))
- Fixed error when trying to get instance if object is deleted \#571 [\#574](https://github.com/jazzband/django-simple-history/pull/574) ([yakimka](https://github.com/yakimka))
- Updated readme to include django 2.2... Ooops [\#573](https://github.com/jazzband/django-simple-history/pull/573) ([rossmechanic](https://github.com/rossmechanic))

## [2.7.3](https://github.com/jazzband/django-simple-history/tree/2.7.3) (2019-07-15)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.7.2...2.7.3)

**Closed issues:**

- Problem upgrading from 1.9.0 to 2.5.0 [\#570](https://github.com/jazzband/django-simple-history/issues/570)
- How to register model with SimpleHistoryAdmin and custom search\_fields? [\#569](https://github.com/jazzband/django-simple-history/issues/569)
- How to use history\_change\_reason [\#567](https://github.com/jazzband/django-simple-history/issues/567)
- Hide History based on User type [\#566](https://github.com/jazzband/django-simple-history/issues/566)
- Model instances with HistoricalRecords do not have changeReason attribute  [\#563](https://github.com/jazzband/django-simple-history/issues/563)
- most\_recent with excluded\_fields sets values incorrectly [\#561](https://github.com/jazzband/django-simple-history/issues/561)
- BigAutoField not mirrored as bigint in historical copy of table [\#556](https://github.com/jazzband/django-simple-history/issues/556)
- Limit history rows [\#554](https://github.com/jazzband/django-simple-history/issues/554)
- Unable to create HistoricalUser record on a separate database [\#538](https://github.com/jazzband/django-simple-history/issues/538)

**Merged pull requests:**

- Bump version to 2.7.3 [\#572](https://github.com/jazzband/django-simple-history/pull/572) ([rossmechanic](https://github.com/rossmechanic))
- Fixed bug in most\_recent\(\) where excluded\_fields weren't handled correctly [\#562](https://github.com/jazzband/django-simple-history/pull/562) ([AmandaCLNg](https://github.com/AmandaCLNg))
- BigAutoField not mirrored as bigint in historical copy of table \#556 [\#560](https://github.com/jazzband/django-simple-history/pull/560) ([partimer](https://github.com/partimer))
- Added multi-table inheritance docs [\#559](https://github.com/jazzband/django-simple-history/pull/559) ([ncvc](https://github.com/ncvc))
- Fixed docs/multiple\_dbs.rst formatting issue [\#558](https://github.com/jazzband/django-simple-history/pull/558) ([ncvc](https://github.com/ncvc))
- Added Django 2.2 to testing matrix [\#555](https://github.com/jazzband/django-simple-history/pull/555) ([rossmechanic](https://github.com/rossmechanic))
- Catch render\(\) call, to allow overriding. [\#530](https://github.com/jazzband/django-simple-history/pull/530) ([Skeen](https://github.com/Skeen))

## [2.7.2](https://github.com/jazzband/django-simple-history/tree/2.7.2) (2019-04-17)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.7.1...2.7.2)

**Closed issues:**

- ModuleNotFoundError: No module named 'six' [\#552](https://github.com/jazzband/django-simple-history/issues/552)
- Can't retrieve absolute URL of history objects [\#551](https://github.com/jazzband/django-simple-history/issues/551)

**Merged pull requests:**

- Patch for ModuleNotFound issue with `six` [\#553](https://github.com/jazzband/django-simple-history/pull/553) ([rossmechanic](https://github.com/rossmechanic))

## [2.7.1](https://github.com/jazzband/django-simple-history/tree/2.7.1) (2019-04-16)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.7.0...2.7.1)

**Fixed bugs:**

- clean\_duplicate\_history doesn't respect history field name [\#540](https://github.com/jazzband/django-simple-history/issues/540)
- most\_recent cannot be combined with excluded\_fields [\#333](https://github.com/jazzband/django-simple-history/issues/333)
- Tracking model with FK to itself.  [\#312](https://github.com/jazzband/django-simple-history/issues/312)

**Closed issues:**

- Patch release for `use_base_model_db` [\#545](https://github.com/jazzband/django-simple-history/issues/545)
- Historical record created when only excluded field changes [\#543](https://github.com/jazzband/django-simple-history/issues/543)
- What is the best way to track Read events on operational models? [\#541](https://github.com/jazzband/django-simple-history/issues/541)
- History Info for Django User Related Tables [\#535](https://github.com/jazzband/django-simple-history/issues/535)
- Specify history\_type for custom model methods [\#534](https://github.com/jazzband/django-simple-history/issues/534)
- Foreign Key value in \_\_str\_\_ results in error. [\#533](https://github.com/jazzband/django-simple-history/issues/533)
- get model history table name [\#531](https://github.com/jazzband/django-simple-history/issues/531)
- I try django-simple-history with django 2.1.4 but it is showing internal server error.  [\#525](https://github.com/jazzband/django-simple-history/issues/525)
- Error when method \_\_str\_\_ points to a foreign key [\#521](https://github.com/jazzband/django-simple-history/issues/521)
- Setting user\_related\_name results in strange migrations in v2.6.0 [\#520](https://github.com/jazzband/django-simple-history/issues/520)
- Does DSH work with factory\_boy ? [\#519](https://github.com/jazzband/django-simple-history/issues/519)
- Model with field named 'instance' does not have the instance field in the history table [\#221](https://github.com/jazzband/django-simple-history/issues/221)
- Correct generic way to use into generic class based views [\#180](https://github.com/jazzband/django-simple-history/issues/180)
- ForeignKeys get not resolved when using all\(\) [\#67](https://github.com/jazzband/django-simple-history/issues/67)

**Merged pull requests:**

- Cleaned up create\_historical\_record call [\#550](https://github.com/jazzband/django-simple-history/pull/550) ([rossmechanic](https://github.com/rossmechanic))
- Bump version to 2.7.1 [\#549](https://github.com/jazzband/django-simple-history/pull/549) ([rossmechanic](https://github.com/rossmechanic))
- Fix non-backward compatible issue from 2.7.0 from GH-507 [\#547](https://github.com/jazzband/django-simple-history/pull/547) ([rossmechanic](https://github.com/rossmechanic))
- Fix hardcoded history manager [\#542](https://github.com/jazzband/django-simple-history/pull/542) ([yetanotherape](https://github.com/yetanotherape))
- Allow the use of multiple databases [\#539](https://github.com/jazzband/django-simple-history/pull/539) ([dopatraman](https://github.com/dopatraman))
- added the possibility to create a relation to the original model [\#536](https://github.com/jazzband/django-simple-history/pull/536) ([nick-traeger](https://github.com/nick-traeger))
- replace deprecated django.utils.six with six [\#526](https://github.com/jazzband/django-simple-history/pull/526) ([erikvw](https://github.com/erikvw))
- GH-221: Added reserved names to docs [\#523](https://github.com/jazzband/django-simple-history/pull/523) ([rossmechanic](https://github.com/rossmechanic))
- Support passing a callable in "custom\_model\_name" feature [\#490](https://github.com/jazzband/django-simple-history/pull/490) ([uhurusurfa](https://github.com/uhurusurfa))

## [2.7.0](https://github.com/jazzband/django-simple-history/tree/2.7.0) (2019-01-16)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.6.0...2.7.0)

**Implemented enhancements:**

- List of changed fields [\#336](https://github.com/jazzband/django-simple-history/issues/336)
- Deleting select historical records [\#313](https://github.com/jazzband/django-simple-history/issues/313)
- Inlines for related historical objects [\#232](https://github.com/jazzband/django-simple-history/issues/232)
- Add Many-to-Many support [\#16](https://github.com/jazzband/django-simple-history/issues/16)

**Fixed bugs:**

- simple-history 2.6.0 generates a migration while 2.5.1 doesn't [\#512](https://github.com/jazzband/django-simple-history/issues/512)
- Django simple history needs database connection to load the models [\#219](https://github.com/jazzband/django-simple-history/issues/219)
- GH-512: allow foreign key to reference self using self str [\#513](https://github.com/jazzband/django-simple-history/pull/513) ([rossmechanic](https://github.com/rossmechanic))

**Closed issues:**

- how could  I get all history queyset? [\#514](https://github.com/jazzband/django-simple-history/issues/514)
- UUID causes first, last, prev\_record, next\_record to be incorrectly ordered [\#504](https://github.com/jazzband/django-simple-history/issues/504)
- Model history list missing in Django-admin panel [\#503](https://github.com/jazzband/django-simple-history/issues/503)
- Override history field [\#429](https://github.com/jazzband/django-simple-history/issues/429)
- invalid literal for int\(\) with base 10: 'a string' when using hashid fields. [\#337](https://github.com/jazzband/django-simple-history/issues/337)
- Start tracking AUTHORS more effectively [\#285](https://github.com/jazzband/django-simple-history/issues/285)
- Any call to manage.py will fail if no default database is specified [\#264](https://github.com/jazzband/django-simple-history/issues/264)
- Error when performing a cascading delete on models with foreign keys [\#185](https://github.com/jazzband/django-simple-history/issues/185)
- Add note in docs for creating history migrations [\#177](https://github.com/jazzband/django-simple-history/issues/177)
- Fields deleted on migration [\#169](https://github.com/jazzband/django-simple-history/issues/169)

**Merged pull requests:**

- Bump version to 2.7.0 [\#517](https://github.com/jazzband/django-simple-history/pull/517) ([rossmechanic](https://github.com/rossmechanic))
- Remove get\_excluded\_fields function from manager – shouldn't be part … [\#515](https://github.com/jazzband/django-simple-history/pull/515) ([rossmechanic](https://github.com/rossmechanic))
- Allow user to be tracked by explicit ID [\#511](https://github.com/jazzband/django-simple-history/pull/511) ([rossmechanic](https://github.com/rossmechanic))
- Initial reorg of docs [\#510](https://github.com/jazzband/django-simple-history/pull/510) ([rossmechanic](https://github.com/rossmechanic))
- Updated CHANGES.rst file with fixes [\#509](https://github.com/jazzband/django-simple-history/pull/509) ([rossmechanic](https://github.com/rossmechanic))
- create historical instance with respect to using\(\) for multidb enviro… [\#507](https://github.com/jazzband/django-simple-history/pull/507) ([erikvw](https://github.com/erikvw))
- Removed .landscape.yml file since landscape.io is deprecated [\#506](https://github.com/jazzband/django-simple-history/pull/506) ([rossmechanic](https://github.com/rossmechanic))
- Update license to show bsd 3 on homepage [\#505](https://github.com/jazzband/django-simple-history/pull/505) ([rossmechanic](https://github.com/rossmechanic))
- Duplicate history cleanup [\#483](https://github.com/jazzband/django-simple-history/pull/483) ([fopina](https://github.com/fopina))
- Don't resolve relationships for history objects [\#479](https://github.com/jazzband/django-simple-history/pull/479) ([RealOrangeOne](https://github.com/RealOrangeOne))
- Most recent with excluded fields [\#477](https://github.com/jazzband/django-simple-history/pull/477) ([Alig1493](https://github.com/Alig1493))

## [2.6.0](https://github.com/jazzband/django-simple-history/tree/2.6.0) (2018-12-12)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.5.1...2.6.0)

**Implemented enhancements:**

- Conflicting models [\#345](https://github.com/jazzband/django-simple-history/issues/345)
- Delete old Historical Records [\#198](https://github.com/jazzband/django-simple-history/issues/198)

**Fixed bugs:**

- Setting app\_label different to model class  [\#485](https://github.com/jazzband/django-simple-history/issues/485)
- django-simple-history does not respect 'deconstruct' kwargs for custom foreignkey fields [\#431](https://github.com/jazzband/django-simple-history/issues/431)
- Warn when using HistoricalRecords on an abstract class without inherit=True [\#341](https://github.com/jazzband/django-simple-history/issues/341)
- admin.site.site\_header not respected [\#205](https://github.com/jazzband/django-simple-history/issues/205)

**Closed issues:**

- Can't use .prev\_record and .next\_record when using not default field name [\#500](https://github.com/jazzband/django-simple-history/issues/500)
- Showing history in admin causes n+1 queries for history\_user [\#495](https://github.com/jazzband/django-simple-history/issues/495)
- support customise history date base on request context [\#487](https://github.com/jazzband/django-simple-history/issues/487)
- Admin template issues on django trunk  [\#473](https://github.com/jazzband/django-simple-history/issues/473)
- 'Options' object has no attribute 'simple\_history\_manager\_attribute' [\#465](https://github.com/jazzband/django-simple-history/issues/465)
- Registration cycle with custom and historized User model and simple-history 2.5.0 [\#459](https://github.com/jazzband/django-simple-history/issues/459)
- Add test config for Python 3.7 [\#453](https://github.com/jazzband/django-simple-history/issues/453)
- Add Black auto formatter [\#446](https://github.com/jazzband/django-simple-history/issues/446)
- Add history\_instance to pre\_create\_historical\_record signal [\#437](https://github.com/jazzband/django-simple-history/issues/437)
- HistoricalRecords' iterator fails when used with 'excluded\_fields' and 'inherit=True' [\#436](https://github.com/jazzband/django-simple-history/issues/436)
- Record the IP Address that made a change [\#421](https://github.com/jazzband/django-simple-history/issues/421)
- Custom history field names [\#328](https://github.com/jazzband/django-simple-history/issues/328)
- Using populate\_history so it works better with migrations [\#326](https://github.com/jazzband/django-simple-history/issues/326)
- South data migration does not make new history record [\#153](https://github.com/jazzband/django-simple-history/issues/153)
- Add comprehensive tests for historical model location/name [\#88](https://github.com/jazzband/django-simple-history/issues/88)

**Merged pull requests:**

- Bump version to 2.6.0 [\#502](https://github.com/jazzband/django-simple-history/pull/502) ([rossmechanic](https://github.com/rossmechanic))
- Fixed bug that prevented next\_record and prev\_record from using custo… [\#501](https://github.com/jazzband/django-simple-history/pull/501) ([rossmechanic](https://github.com/rossmechanic))
- Add extra context to admin [\#499](https://github.com/jazzband/django-simple-history/pull/499) ([barm](https://github.com/barm))
- Ordered AUTHORS.rst and added docs badge [\#497](https://github.com/jazzband/django-simple-history/pull/497) ([rossmechanic](https://github.com/rossmechanic))
- Select related users when displaying history in admin [\#496](https://github.com/jazzband/django-simple-history/pull/496) ([rudkjobing](https://github.com/rudkjobing))
- Added Python 3.7 to testing matrix [\#494](https://github.com/jazzband/django-simple-history/pull/494) ([rossmechanic](https://github.com/rossmechanic))
- Removed 'health' badge and added 'maintainability' badge [\#493](https://github.com/jazzband/django-simple-history/pull/493) ([rossmechanic](https://github.com/rossmechanic))
- Ignore test files for codeclimate checks [\#492](https://github.com/jazzband/django-simple-history/pull/492) ([rossmechanic](https://github.com/rossmechanic))
- Initial code-climate config [\#491](https://github.com/jazzband/django-simple-history/pull/491) ([rossmechanic](https://github.com/rossmechanic))
- Added CHANGES and AUTHORS to checklist in PR template [\#488](https://github.com/jazzband/django-simple-history/pull/488) ([rossmechanic](https://github.com/rossmechanic))
- Set app label via instantiation of historical records [\#486](https://github.com/jazzband/django-simple-history/pull/486) ([uhurusurfa](https://github.com/uhurusurfa))
- Adds german translations [\#484](https://github.com/jazzband/django-simple-history/pull/484) ([funkyfuture](https://github.com/funkyfuture))
- Update README.rst to use svg badge instead of png [\#482](https://github.com/jazzband/django-simple-history/pull/482) ([rossmechanic](https://github.com/rossmechanic))
- Added downloads badge and code style badge [\#481](https://github.com/jazzband/django-simple-history/pull/481) ([rossmechanic](https://github.com/rossmechanic))
- GH-446: add black auto-formatter [\#480](https://github.com/jazzband/django-simple-history/pull/480) ([rossmechanic](https://github.com/rossmechanic))
- Fix admin template issues on django trunk [\#474](https://github.com/jazzband/django-simple-history/pull/474) ([rossmechanic](https://github.com/rossmechanic))
- GH-341: Warning if HistoricalRecords\(inherit=False\) in an abstract class [\#472](https://github.com/jazzband/django-simple-history/pull/472) ([rossmechanic](https://github.com/rossmechanic))
- Send history\_instance in the `pre_create_historical_record` signal [\#471](https://github.com/jazzband/django-simple-history/pull/471) ([kseever](https://github.com/kseever))
- Prefetch which fields instances have [\#470](https://github.com/jazzband/django-simple-history/pull/470) ([RealOrangeOne](https://github.com/RealOrangeOne))
- Fiz tiny little typo that messes on advanced.rst [\#468](https://github.com/jazzband/django-simple-history/pull/468) ([chaws](https://github.com/chaws))
- Fix flake8 error and pin flake8 to 3.6.0 [\#466](https://github.com/jazzband/django-simple-history/pull/466) ([rossmechanic](https://github.com/rossmechanic))
- Ensure custom arguments for fields are included in historical models' fields [\#462](https://github.com/jazzband/django-simple-history/pull/462) ([tbeadle](https://github.com/tbeadle))
- add custom\_model\_name to HistoricalRecords [\#451](https://github.com/jazzband/django-simple-history/pull/451) ([ChrisZhangCadre](https://github.com/ChrisZhangCadre))
- Honor a custom admin site\_header in the listing and details pages. [\#448](https://github.com/jazzband/django-simple-history/pull/448) ([tbeadle](https://github.com/tbeadle))

## [2.5.1](https://github.com/jazzband/django-simple-history/tree/2.5.1) (2018-10-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.5.0...2.5.1)

**Closed issues:**

- Improve bulk\_history\_create [\#442](https://github.com/jazzband/django-simple-history/issues/442)
- In  the admin, in the history the history\_change\_reason is not displayed [\#427](https://github.com/jazzband/django-simple-history/issues/427)

**Merged pull requests:**

- Fix custom user bug and update to 2.5.1 [\#460](https://github.com/jazzband/django-simple-history/pull/460) ([rossmechanic](https://github.com/rossmechanic))
- Issue \#427 added history\_change\_reason to the history list view as a … [\#458](https://github.com/jazzband/django-simple-history/pull/458) ([JimGomez48](https://github.com/JimGomez48))
- Support changeReason for bulk history create [\#449](https://github.com/jazzband/django-simple-history/pull/449) ([lmiguelvargasf](https://github.com/lmiguelvargasf))

## [2.5.0](https://github.com/jazzband/django-simple-history/tree/2.5.0) (2018-10-18)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.4.0...2.5.0)

**Closed issues:**

- Allow historical data to be deleted when the master record is deleted [\#439](https://github.com/jazzband/django-simple-history/issues/439)
- Model field values change after putting `excluded_fields` in HistoricalRecords [\#433](https://github.com/jazzband/django-simple-history/issues/433)

**Merged pull requests:**

- Update docs to fix typo p2 [\#454](https://github.com/jazzband/django-simple-history/pull/454) ([barm](https://github.com/barm))
- Update docs to fix typo [\#452](https://github.com/jazzband/django-simple-history/pull/452) ([barm](https://github.com/barm))
- Update changelog [\#450](https://github.com/jazzband/django-simple-history/pull/450) ([barm](https://github.com/barm))
- added Russian localization [\#441](https://github.com/jazzband/django-simple-history/pull/441) ([ozeranskiy](https://github.com/ozeranskiy))
- Add feature to allow historical records to be deleted when master is deleted [\#440](https://github.com/jazzband/django-simple-history/pull/440) ([rwlogel](https://github.com/rwlogel))
- Fix/better user model determination [\#435](https://github.com/jazzband/django-simple-history/pull/435) ([seawolf42](https://github.com/seawolf42))

## [2.4.0](https://github.com/jazzband/django-simple-history/tree/2.4.0) (2018-09-20)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.3.0...2.4.0)

**Implemented enhancements:**

- Give ability to compare two history versions [\#54](https://github.com/jazzband/django-simple-history/issues/54)

**Closed issues:**

- Warn when using HistoricalRecords on a class by inherit=True and a class inherited by proxy=True [\#425](https://github.com/jazzband/django-simple-history/issues/425)
- Migration crash on alter to unique [\#424](https://github.com/jazzband/django-simple-history/issues/424)
- Performance optimization for populate\_history [\#423](https://github.com/jazzband/django-simple-history/issues/423)
- Ensure history integrity for audit use case [\#420](https://github.com/jazzband/django-simple-history/issues/420)
- Relate generated Historical\_x model to their base model [\#419](https://github.com/jazzband/django-simple-history/issues/419)

**Merged pull requests:**

- Prepare for 2.4.0 release [\#434](https://github.com/jazzband/django-simple-history/pull/434) ([rossmechanic](https://github.com/rossmechanic))
- Remove support for MongoDB [\#432](https://github.com/jazzband/django-simple-history/pull/432) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Fix typo in docs [\#430](https://github.com/jazzband/django-simple-history/pull/430) ([roddds](https://github.com/roddds))
- Added database version to bug report template [\#428](https://github.com/jazzband/django-simple-history/pull/428) ([rossmechanic](https://github.com/rossmechanic))
- Add pre and post create\_historical\_record signals [\#426](https://github.com/jazzband/django-simple-history/pull/426) ([mscansian](https://github.com/mscansian))
- Add support for Django 2.1 [\#418](https://github.com/jazzband/django-simple-history/pull/418) ([ThePumpingLemma](https://github.com/ThePumpingLemma))
- Document some register attributes [\#417](https://github.com/jazzband/django-simple-history/pull/417) ([dgilge](https://github.com/dgilge))

## [2.3.0](https://github.com/jazzband/django-simple-history/tree/2.3.0) (2018-07-19)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.2.0...2.3.0)

**Implemented enhancements:**

- Add a "ModelDelta" and "\_\_sub\_\_" method to have a timeline info [\#244](https://github.com/jazzband/django-simple-history/issues/244)

**Fixed bugs:**

- The no-user placeholder in object history template is not translated [\#240](https://github.com/jazzband/django-simple-history/issues/240)

**Closed issues:**

- History should not be created when model is not dirty [\#386](https://github.com/jazzband/django-simple-history/issues/386)
- Mysql server gone away on populating history [\#327](https://github.com/jazzband/django-simple-history/issues/327)
- Foreign Key Constraint fails from unit tests [\#216](https://github.com/jazzband/django-simple-history/issues/216)

**Merged pull requests:**

- Implement the ability to diff HistoricalRecords [\#416](https://github.com/jazzband/django-simple-history/pull/416) ([kseever](https://github.com/kseever))

## [2.2.0](https://github.com/jazzband/django-simple-history/tree/2.2.0) (2018-07-02)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.1.1...2.2.0)

**Implemented enhancements:**

- Saving history on batch\_create [\#380](https://github.com/jazzband/django-simple-history/issues/380)
- History creation fails if request.user isn't an AUTH\_USER\_MODEL [\#245](https://github.com/jazzband/django-simple-history/issues/245)
- Using django-simple-history to track history of change of specific field of model [\#199](https://github.com/jazzband/django-simple-history/issues/199)

**Fixed bugs:**

- HistoricalObjectDescriptor throws exception with excluded\_fields [\#310](https://github.com/jazzband/django-simple-history/issues/310)

**Closed issues:**

- Update for Django 2.1 [\#394](https://github.com/jazzband/django-simple-history/issues/394)
- Problem with F\(\) objects [\#382](https://github.com/jazzband/django-simple-history/issues/382)
- Querysets as\_for [\#354](https://github.com/jazzband/django-simple-history/issues/354)
- Audit trail feature [\#349](https://github.com/jazzband/django-simple-history/issues/349)
- History of custom UserModel  [\#344](https://github.com/jazzband/django-simple-history/issues/344)
- Include license information in metadata [\#321](https://github.com/jazzband/django-simple-history/issues/321)
- Using taggit together with simple history makes migrations non-portable [\#317](https://github.com/jazzband/django-simple-history/issues/317)
- Changing history in the admin creates new history objects, rather than updating past history objects. [\#254](https://github.com/jazzband/django-simple-history/issues/254)
- FieldError: Cannot resolve keyword 'history' into field. [\#249](https://github.com/jazzband/django-simple-history/issues/249)
- Update documentation about how simple history does not log history when .update\(\) or bulk\_create are used [\#174](https://github.com/jazzband/django-simple-history/issues/174)

**Merged pull requests:**

- Bumped to 2.2.0 [\#415](https://github.com/jazzband/django-simple-history/pull/415) ([rossmechanic](https://github.com/rossmechanic))
- Updated documentation for queryset updates [\#414](https://github.com/jazzband/django-simple-history/pull/414) ([rossmechanic](https://github.com/rossmechanic))
- Update documentation on F\(\) expressions [\#413](https://github.com/jazzband/django-simple-history/pull/413) ([rossmechanic](https://github.com/rossmechanic))
- GH-380: Save history on bulk\_create [\#412](https://github.com/jazzband/django-simple-history/pull/412) ([rossmechanic](https://github.com/rossmechanic))
- Allow alternative user model for tracking history\_user [\#371](https://github.com/jazzband/django-simple-history/pull/371) ([rwlogel](https://github.com/rwlogel))

## [2.1.1](https://github.com/jazzband/django-simple-history/tree/2.1.1) (2018-06-15)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.1.0...2.1.1)

**Fixed bugs:**

- Problem to use history = HistoricalRecords\(excluded\_fields=\['description'\]\) [\#402](https://github.com/jazzband/django-simple-history/issues/402)

**Closed issues:**

- Feature to track changes only and not the creation part. [\#409](https://github.com/jazzband/django-simple-history/issues/409)
- prefetch\_related on historical model [\#407](https://github.com/jazzband/django-simple-history/issues/407)
- populate\_history uses an incorrect Manager [\#239](https://github.com/jazzband/django-simple-history/issues/239)

**Merged pull requests:**

- Bumping version to 2.1.1 [\#411](https://github.com/jazzband/django-simple-history/pull/411) ([rossmechanic](https://github.com/rossmechanic))
- Don't populate excluded fields in populate history [\#410](https://github.com/jazzband/django-simple-history/pull/410) ([rossmechanic](https://github.com/rossmechanic))
- Fix out of memory exception in populate\_history management command [\#408](https://github.com/jazzband/django-simple-history/pull/408) ([rossmechanic](https://github.com/rossmechanic))
- Small tweaks to test names for history change reason [\#406](https://github.com/jazzband/django-simple-history/pull/406) ([kseever](https://github.com/kseever))
- Create CODE\_OF\_CONDUCT.md [\#405](https://github.com/jazzband/django-simple-history/pull/405) ([rossmechanic](https://github.com/rossmechanic))

## [2.1.0](https://github.com/jazzband/django-simple-history/tree/2.1.0) (2018-06-04)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/2.0...2.1.0)

**Implemented enhancements:**

- Inadequate length for the 'history\_change\_reason' field [\#378](https://github.com/jazzband/django-simple-history/issues/378)
- Query previous/next historical entry [\#230](https://github.com/jazzband/django-simple-history/issues/230)
- Add a 'batch\_size' option to the populate history command [\#202](https://github.com/jazzband/django-simple-history/issues/202)
- Exclude fields? [\#165](https://github.com/jazzband/django-simple-history/issues/165)
- Override history ID? [\#116](https://github.com/jazzband/django-simple-history/issues/116)

**Fixed bugs:**

- Out-of-memory-exception when populating history with management command [\#398](https://github.com/jazzband/django-simple-history/issues/398)
- django-simple-history middleware issue [\#369](https://github.com/jazzband/django-simple-history/issues/369)

**Closed issues:**

- Cannot get "tags" from "taggit" to save history changes [\#395](https://github.com/jazzband/django-simple-history/issues/395)
- Getting migration into own code when registering external app [\#393](https://github.com/jazzband/django-simple-history/issues/393)
- override the change\_form to add few more dependency to display markdown editor in form [\#389](https://github.com/jazzband/django-simple-history/issues/389)
- Middleware cleanup failure [\#387](https://github.com/jazzband/django-simple-history/issues/387)
- Show what field of model was changed [\#383](https://github.com/jazzband/django-simple-history/issues/383)
- On migrate Error: ImportError: No module named 'django.urls' [\#375](https://github.com/jazzband/django-simple-history/issues/375)
- The process of using simple\_history.register to history-track the User model is NOT working [\#372](https://github.com/jazzband/django-simple-history/issues/372)
- HistoricalFoo model is defined in wrong module path [\#343](https://github.com/jazzband/django-simple-history/issues/343)
- How to revert model outside the admin [\#322](https://github.com/jazzband/django-simple-history/issues/322)
- not support update function ? [\#309](https://github.com/jazzband/django-simple-history/issues/309)
- Created manual history records [\#307](https://github.com/jazzband/django-simple-history/issues/307)
- Example  [\#305](https://github.com/jazzband/django-simple-history/issues/305)
- Address warnings from Django 1.11 [\#291](https://github.com/jazzband/django-simple-history/issues/291)
- "no such column" error [\#290](https://github.com/jazzband/django-simple-history/issues/290)
- Consider moving this project to jazzband [\#282](https://github.com/jazzband/django-simple-history/issues/282)
- How to set creation date on imported objects? [\#272](https://github.com/jazzband/django-simple-history/issues/272)
- Revert option in custom page [\#268](https://github.com/jazzband/django-simple-history/issues/268)
- Does simple-history work well with soft deletes? If so, which soft-deletes library you recommend? [\#260](https://github.com/jazzband/django-simple-history/issues/260)
- simple\_history\object\_history.html \(Source does not exist\) [\#228](https://github.com/jazzband/django-simple-history/issues/228)
- cannot register simple-history if using modeladmin customization  [\#227](https://github.com/jazzband/django-simple-history/issues/227)
- Support custom auth [\#226](https://github.com/jazzband/django-simple-history/issues/226)
- Wrong table name when using abstract models [\#224](https://github.com/jazzband/django-simple-history/issues/224)
- Querying on all models that implement history? [\#223](https://github.com/jazzband/django-simple-history/issues/223)
- Can't access history of User from  /admin/auth/user/  [\#222](https://github.com/jazzband/django-simple-history/issues/222)
- Annotations or comments in the history table [\#214](https://github.com/jazzband/django-simple-history/issues/214)
- History table contains correct user but admin page shows 'admin' [\#210](https://github.com/jazzband/django-simple-history/issues/210)
- AttributeError: 'module' object has no attribute 'CustomForeignKeyField' [\#208](https://github.com/jazzband/django-simple-history/issues/208)
- Avoid historical entry on delete [\#207](https://github.com/jazzband/django-simple-history/issues/207)
- Recover history programatically [\#176](https://github.com/jazzband/django-simple-history/issues/176)

**Merged pull requests:**

- Bumped version to 2.1.0 [\#404](https://github.com/jazzband/django-simple-history/pull/404) ([rossmechanic](https://github.com/rossmechanic))
- Backward compatible middleware [\#403](https://github.com/jazzband/django-simple-history/pull/403) ([iamanikeev](https://github.com/iamanikeev))
- Create PULL\_REQUEST\_TEMPLATE.md [\#401](https://github.com/jazzband/django-simple-history/pull/401) ([rossmechanic](https://github.com/rossmechanic))
- Update issue templates [\#400](https://github.com/jazzband/django-simple-history/pull/400) ([rossmechanic](https://github.com/rossmechanic))
- Added documentation for failures resulting from django-webtest [\#392](https://github.com/jazzband/django-simple-history/pull/392) ([rossmechanic](https://github.com/rossmechanic))
- Set attribute on history list entries, from evaluated admin methods [\#390](https://github.com/jazzband/django-simple-history/pull/390) ([blawson](https://github.com/blawson))
- Update usage.rst [\#384](https://github.com/jazzband/django-simple-history/pull/384) ([pmontepagano](https://github.com/pmontepagano))
- Feature/issue 379 history change reason [\#379](https://github.com/jazzband/django-simple-history/pull/379) ([krisneuharth](https://github.com/krisneuharth))
- Added docs for reverting a model [\#377](https://github.com/jazzband/django-simple-history/pull/377) ([rossmechanic](https://github.com/rossmechanic))
- Added documentation about the different ways to record which user cha… [\#376](https://github.com/jazzband/django-simple-history/pull/376) ([rossmechanic](https://github.com/rossmechanic))
- Spelling. [\#374](https://github.com/jazzband/django-simple-history/pull/374) ([vshih](https://github.com/vshih))
- Provide history\_id\_field to change the field type for history\_id [\#368](https://github.com/jazzband/django-simple-history/pull/368) ([rwlogel](https://github.com/rwlogel))
- Removed reference to south package. [\#367](https://github.com/jazzband/django-simple-history/pull/367) ([wizpig64](https://github.com/wizpig64))
- Fixed linting errors and setup flake8 to run on travis [\#366](https://github.com/jazzband/django-simple-history/pull/366) ([rossmechanic](https://github.com/rossmechanic))
- feat\(HistoryRecords\): prev and next attributes [\#365](https://github.com/jazzband/django-simple-history/pull/365) ([SpainTrain](https://github.com/SpainTrain))
- Polish translations update [\#283](https://github.com/jazzband/django-simple-history/pull/283) ([grzegorzbialy](https://github.com/grzegorzbialy))

## [2.0](https://github.com/jazzband/django-simple-history/tree/2.0) (2018-04-05)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.9.1...2.0)

**Closed issues:**

- ModuleNotFoundError: No module named 'django.core.urlresolvers' [\#359](https://github.com/jazzband/django-simple-history/issues/359)
- admin does not show history records [\#357](https://github.com/jazzband/django-simple-history/issues/357)
- Dropping Support for Django \< 1.11 [\#356](https://github.com/jazzband/django-simple-history/issues/356)
- AttributeError when using historical querysets with Django REST framework [\#332](https://github.com/jazzband/django-simple-history/issues/332)
- Django 2.0 compatibility [\#330](https://github.com/jazzband/django-simple-history/issues/330)
- Tracking an inherited model \(abstract class\) [\#269](https://github.com/jazzband/django-simple-history/issues/269)
- Middleware documentation clarification [\#265](https://github.com/jazzband/django-simple-history/issues/265)

**Merged pull requests:**

- Fixed HistoryRequestMiddleware so that it works with Django version \>= 1.10 [\#364](https://github.com/jazzband/django-simple-history/pull/364) ([rossmechanic](https://github.com/rossmechanic))
- More Django 1.9 leftovers [\#363](https://github.com/jazzband/django-simple-history/pull/363) ([wizpig64](https://github.com/wizpig64))
- Removed support for Django 1.9 [\#362](https://github.com/jazzband/django-simple-history/pull/362) ([rossmechanic](https://github.com/rossmechanic))
- Added has\_change\_permission check to SimpleHistoryAdmin.history\_view [\#361](https://github.com/jazzband/django-simple-history/pull/361) ([ncvc](https://github.com/ncvc))
- Removed Django 1.8 support [\#360](https://github.com/jazzband/django-simple-history/pull/360) ([rossmechanic](https://github.com/rossmechanic))
- Remove support for Django 1.7 [\#358](https://github.com/jazzband/django-simple-history/pull/358) ([rossmechanic](https://github.com/rossmechanic))

## [1.9.1](https://github.com/jazzband/django-simple-history/tree/1.9.1) (2018-03-30)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.9.0...1.9.1)

**Closed issues:**

- Custom comment [\#350](https://github.com/jazzband/django-simple-history/issues/350)
- Need for maintainers? [\#348](https://github.com/jazzband/django-simple-history/issues/348)
- Which is the maximum number o characters of change reason? Can I change it? [\#346](https://github.com/jazzband/django-simple-history/issues/346)
- superuser get users operation of model？ [\#342](https://github.com/jazzband/django-simple-history/issues/342)
- Retrieve attributes of a history object [\#339](https://github.com/jazzband/django-simple-history/issues/339)
- Add history to a model via a base class [\#329](https://github.com/jazzband/django-simple-history/issues/329)
- Accessing Model Methods [\#311](https://github.com/jazzband/django-simple-history/issues/311)
- Can't Access the History Detail View of /app/model/\<pk\>/history/\<history\_id\> [\#308](https://github.com/jazzband/django-simple-history/issues/308)
- Missing Column: history\_change\_reason [\#300](https://github.com/jazzband/django-simple-history/issues/300)
- query history giving odd results \(django 1.10\) [\#298](https://github.com/jazzband/django-simple-history/issues/298)
- Are many to many model fields supported? [\#297](https://github.com/jazzband/django-simple-history/issues/297)
- Link to crate.io is gone [\#294](https://github.com/jazzband/django-simple-history/issues/294)
- Documentation item "save without historical record" doesn't render properly [\#293](https://github.com/jazzband/django-simple-history/issues/293)
- Drop Django 1.6 and Python 3.3 [\#292](https://github.com/jazzband/django-simple-history/issues/292)
- Change ugettext to ugettext\_lazy? [\#288](https://github.com/jazzband/django-simple-history/issues/288)
- Exception on UUID ForeignKey [\#278](https://github.com/jazzband/django-simple-history/issues/278)

**Merged pull requests:**

- Fixes issue with tracking an inherited model [\#355](https://github.com/jazzband/django-simple-history/pull/355) ([rossmechanic](https://github.com/rossmechanic))
-  Drop EOL Django 1.6 and Python 3.3 [\#334](https://github.com/jazzband/django-simple-history/pull/334) ([hugovk](https://github.com/hugovk))
- Fixes history detail view for concrete models that instantiate abstract historical models defined in separate apps [\#323](https://github.com/jazzband/django-simple-history/pull/323) ([rossmechanic](https://github.com/rossmechanic))
- Self referencing field migration fix [\#319](https://github.com/jazzband/django-simple-history/pull/319) ([KevinGrahamFoster](https://github.com/KevinGrahamFoster))
- Add note about running migrations [\#314](https://github.com/jazzband/django-simple-history/pull/314) ([rca](https://github.com/rca))
- fix mongodb engine check [\#306](https://github.com/jazzband/django-simple-history/pull/306) ([singlerider](https://github.com/singlerider))
- Use get\_queryset rather than model.objects [\#303](https://github.com/jazzband/django-simple-history/pull/303) ([WnP](https://github.com/WnP))
- Switch ugettext to ugettext\_lazy in models.py [\#301](https://github.com/jazzband/django-simple-history/pull/301) ([haikuginger](https://github.com/haikuginger))
- Fix/issue293 [\#296](https://github.com/jazzband/django-simple-history/pull/296) ([evertrol](https://github.com/evertrol))
- Fix dead link in the documentation \[issue 294\] [\#295](https://github.com/jazzband/django-simple-history/pull/295) ([evertrol](https://github.com/evertrol))
- Update readme [\#289](https://github.com/jazzband/django-simple-history/pull/289) ([joshblum](https://github.com/joshblum))
- added save\_without\_historical\_record to documents [\#286](https://github.com/jazzband/django-simple-history/pull/286) ([lee-seul](https://github.com/lee-seul))
- Prepare 1.9.0 Release [\#284](https://github.com/jazzband/django-simple-history/pull/284) ([treyhunner](https://github.com/treyhunner))
- Add missing translations for pt\_BR [\#281](https://github.com/jazzband/django-simple-history/pull/281) ([cuducos](https://github.com/cuducos))
- Fix i18n bugs [\#280](https://github.com/jazzband/django-simple-history/pull/280) ([cuducos](https://github.com/cuducos))
- Add Brazilian Portuguese \(pt\_BR\) translation files [\#279](https://github.com/jazzband/django-simple-history/pull/279) ([cuducos](https://github.com/cuducos))
- added py36 and Django 1.11 to test environments [\#276](https://github.com/jazzband/django-simple-history/pull/276) ([rooterkyberian](https://github.com/rooterkyberian))
- add history change reason to allow reasoning for the changes\[2\] [\#275](https://github.com/jazzband/django-simple-history/pull/275) ([joaojunior](https://github.com/joaojunior))
- Exclude fields [\#274](https://github.com/jazzband/django-simple-history/pull/274) ([joaojunior](https://github.com/joaojunior))
- Convert readthedocs link for their .org -\> .io migration for hosted projects [\#267](https://github.com/jazzband/django-simple-history/pull/267) ([adamchainz](https://github.com/adamchainz))
- Added batch size option to the management command for populating the history [\#263](https://github.com/jazzband/django-simple-history/pull/263) ([macro1](https://github.com/macro1))
- Field list [\#256](https://github.com/jazzband/django-simple-history/pull/256) ([gbataille](https://github.com/gbataille))
- add history change reason to allow reasoning for the changes [\#152](https://github.com/jazzband/django-simple-history/pull/152) ([hmit](https://github.com/hmit))

## [1.9.0](https://github.com/jazzband/django-simple-history/tree/1.9.0) (2017-06-12)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.8.2...1.9.0)

**Closed issues:**

- No module named reportssimple\_history [\#270](https://github.com/jazzband/django-simple-history/issues/270)
- Django 1.10 populate\_history [\#262](https://github.com/jazzband/django-simple-history/issues/262)

## [1.8.2](https://github.com/jazzband/django-simple-history/tree/1.8.2) (2017-01-20)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.8.1...1.8.2)

**Implemented enhancements:**

- HistorialRecords\(\) doesn't seem to work on Abstract models [\#143](https://github.com/jazzband/django-simple-history/issues/143)

**Fixed bugs:**

- DETAIL:  Key \(history\_user\_id\)=\(1\) is not present in table "auth\_user". [\#193](https://github.com/jazzband/django-simple-history/issues/193)

**Closed issues:**

- Test is broken in master  [\#257](https://github.com/jazzband/django-simple-history/issues/257)
- manage.py populate\_history broken with Django 1.10 [\#253](https://github.com/jazzband/django-simple-history/issues/253)
- HistoryRequestMiddleware not defined [\#248](https://github.com/jazzband/django-simple-history/issues/248)
- \[Django 1.10\] CharFields must define a 'max\_length' attribute [\#242](https://github.com/jazzband/django-simple-history/issues/242)
- I try usage in Django 1.10.2 and I am seeing error in runserver [\#241](https://github.com/jazzband/django-simple-history/issues/241)
- django-simple-history plugin doesn't work correctly with django 1.10 admin UI [\#237](https://github.com/jazzband/django-simple-history/issues/237)
- Track only Create \(Not Updates or Deletes\) [\#235](https://github.com/jazzband/django-simple-history/issues/235)
- MIDDLEWARE\_CLASSES setting is deprecated in Django 1.10 [\#234](https://github.com/jazzband/django-simple-history/issues/234)
- change history\_date and history\_user\_id in django admin? [\#220](https://github.com/jazzband/django-simple-history/issues/220)
- 'SimpleHistoryAdmin' has no attribute '\_meta' in Django 1.9.2 [\#218](https://github.com/jazzband/django-simple-history/issues/218)
- Failed Import \(on shell\) [\#215](https://github.com/jazzband/django-simple-history/issues/215)

**Merged pull requests:**

- Add Django 1.10 support [\#259](https://github.com/jazzband/django-simple-history/pull/259) ([macro1](https://github.com/macro1))
- Update usage.rst [\#225](https://github.com/jazzband/django-simple-history/pull/225) ([gabn88](https://github.com/gabn88))
- Polish locale [\#217](https://github.com/jazzband/django-simple-history/pull/217) ([grzegorzbialy](https://github.com/grzegorzbialy))

## [1.8.1](https://github.com/jazzband/django-simple-history/tree/1.8.1) (2016-03-20)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.8.0...1.8.1)

**Closed issues:**

- Does not work with django-modeltranslation [\#209](https://github.com/jazzband/django-simple-history/issues/209)

**Merged pull requests:**

- Unset middleware request [\#213](https://github.com/jazzband/django-simple-history/pull/213) ([lucaswiman](https://github.com/lucaswiman))

## [1.8.0](https://github.com/jazzband/django-simple-history/tree/1.8.0) (2016-02-03)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.7.0...1.8.0)

**Implemented enhancements:**

- Allow history database table to be specified [\#26](https://github.com/jazzband/django-simple-history/issues/26)

**Fixed bugs:**

- changed\_by field with through model\(that already has User ForeignKey\) [\#86](https://github.com/jazzband/django-simple-history/issues/86)

**Closed issues:**

- Simple History Object Tools URL invalid in Django 1.9 [\#206](https://github.com/jazzband/django-simple-history/issues/206)

**Merged pull requests:**

- Allow historical tracking to be set on abstract bases [\#112](https://github.com/jazzband/django-simple-history/pull/112) ([macro1](https://github.com/macro1))

## [1.7.0](https://github.com/jazzband/django-simple-history/tree/1.7.0) (2015-12-03)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.6.3...1.7.0)

**Closed issues:**

- Can't find definition for method `get_previous_by_created_ts`. [\#201](https://github.com/jazzband/django-simple-history/issues/201)
- Missing "simple\_history.templatetags" value in setup.py packages list \(\#197, branch django19\) [\#200](https://github.com/jazzband/django-simple-history/issues/200)
- Handling bulk\_create operations? [\#194](https://github.com/jazzband/django-simple-history/issues/194)
- How to create the appropriate history tables for tracked models [\#192](https://github.com/jazzband/django-simple-history/issues/192)
- History not logged when performing save on "proxy" model [\#191](https://github.com/jazzband/django-simple-history/issues/191)
- Using HistoricalRecords in model with StatusField causes AssertionError from model\_utils [\#190](https://github.com/jazzband/django-simple-history/issues/190)
- SSL SYSCALL error [\#189](https://github.com/jazzband/django-simple-history/issues/189)
- IntegrityError when deleting User with email set to None [\#188](https://github.com/jazzband/django-simple-history/issues/188)
- Model delete [\#178](https://github.com/jazzband/django-simple-history/issues/178)

**Merged pull requests:**

- Remove Django 1.4, and Python 2.6 and 3.2 support [\#203](https://github.com/jazzband/django-simple-history/pull/203) ([macro1](https://github.com/macro1))
- Add Django 1.9 support [\#197](https://github.com/jazzband/django-simple-history/pull/197) ([macro1](https://github.com/macro1))
- Support for custom tables names [\#196](https://github.com/jazzband/django-simple-history/pull/196) ([jleroy](https://github.com/jleroy))
- Add history listing of deleted objects [\#195](https://github.com/jazzband/django-simple-history/pull/195) ([macro1](https://github.com/macro1))
- Add ability to edit history [\#187](https://github.com/jazzband/django-simple-history/pull/187) ([buddylindsey](https://github.com/buddylindsey))

## [1.6.3](https://github.com/jazzband/django-simple-history/tree/1.6.3) (2015-07-31)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.6.2...1.6.3)

**Closed issues:**

- ValueError: invalid literal for int\(\) with base 10 if ForeignKey to\_field is str [\#182](https://github.com/jazzband/django-simple-history/issues/182)
- RemovedInDjango19Warning [\#181](https://github.com/jazzband/django-simple-history/issues/181)
- simple history and migrations in django 1.7 [\#146](https://github.com/jazzband/django-simple-history/issues/146)

**Merged pull requests:**

- Respect the to\_field setting and the target field type [\#186](https://github.com/jazzband/django-simple-history/pull/186) ([arski](https://github.com/arski))
- fix small issue on Makefile [\#183](https://github.com/jazzband/django-simple-history/pull/183) ([luzfcb](https://github.com/luzfcb))
- Switch from coveralls to codecov [\#179](https://github.com/jazzband/django-simple-history/pull/179) ([treyhunner](https://github.com/treyhunner))

## [1.6.2](https://github.com/jazzband/django-simple-history/tree/1.6.2) (2015-07-04)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.6.1...1.6.2)

**Closed issues:**

- timestamps on Change history are wrong [\#175](https://github.com/jazzband/django-simple-history/issues/175)
- Counts of historical records [\#173](https://github.com/jazzband/django-simple-history/issues/173)
- django 18 deprecation warnings [\#170](https://github.com/jazzband/django-simple-history/issues/170)

**Merged pull requests:**

- update imports for Django 1.8; fixes "django 18 deprecation warnings \#170" [\#172](https://github.com/jazzband/django-simple-history/pull/172) ([bradford281](https://github.com/bradford281))

## [1.6.1](https://github.com/jazzband/django-simple-history/tree/1.6.1) (2015-04-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.6.0...1.6.1)

**Fixed bugs:**

- One-to-one relations can cause models.DoesNotExist Error [\#162](https://github.com/jazzband/django-simple-history/issues/162)

**Closed issues:**

- IntegrityError: Using Historical Records on an object that inherits from another non abstract object [\#166](https://github.com/jazzband/django-simple-history/issues/166)
- OneToOneField that's a primary key causes AttributeError [\#164](https://github.com/jazzband/django-simple-history/issues/164)

**Merged pull requests:**

- Fix one-to-one relations in admin and restoring to historical instances [\#168](https://github.com/jazzband/django-simple-history/pull/168) ([macro1](https://github.com/macro1))
- Force OneToOne to be a ForeignKey on historical models [\#167](https://github.com/jazzband/django-simple-history/pull/167) ([macro1](https://github.com/macro1))

## [1.6.0](https://github.com/jazzband/django-simple-history/tree/1.6.0) (2015-04-16)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.5.4...1.6.0)

**Implemented enhancements:**

- Django 1.8: ImportError: No module named related [\#156](https://github.com/jazzband/django-simple-history/issues/156)

**Closed issues:**

- Information about user is lost when user is deleted [\#158](https://github.com/jazzband/django-simple-history/issues/158)
- Error During Template rendering [\#155](https://github.com/jazzband/django-simple-history/issues/155)
- Compatibility with fixtures and initial data [\#93](https://github.com/jazzband/django-simple-history/issues/93)
- save\_without\_historical\_record\(\) Does not work [\#68](https://github.com/jazzband/django-simple-history/issues/68)

**Merged pull requests:**

- Remove default accessor for historical models on auth.User [\#163](https://github.com/jazzband/django-simple-history/pull/163) ([macro1](https://github.com/macro1))
- \[WIP\] Add support for django \< 1.8 [\#161](https://github.com/jazzband/django-simple-history/pull/161) ([rodxavier](https://github.com/rodxavier))
- Add Django 1.8 support [\#160](https://github.com/jazzband/django-simple-history/pull/160) ([macro1](https://github.com/macro1))

## [1.5.4](https://github.com/jazzband/django-simple-history/tree/1.5.4) (2015-02-08)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.5.3...1.5.4)

**Fixed bugs:**

- Problem with custom user and HistoricalRecords [\#85](https://github.com/jazzband/django-simple-history/issues/85)

**Closed issues:**

- Do NOT delete the historical elements when a user is deleted. [\#149](https://github.com/jazzband/django-simple-history/issues/149)
- Question: doing a global query [\#147](https://github.com/jazzband/django-simple-history/issues/147)
- Problems with django\_debug\_toolbar [\#139](https://github.com/jazzband/django-simple-history/issues/139)

**Merged pull requests:**

- Please support latest\(\) [\#151](https://github.com/jazzband/django-simple-history/pull/151) ([rh0dium](https://github.com/rh0dium))
- Do NOT CASCADE delete the history elements when a user gets deleted. [\#150](https://github.com/jazzband/django-simple-history/pull/150) ([rh0dium](https://github.com/rh0dium))
- Indicate non-coverage areas [\#148](https://github.com/jazzband/django-simple-history/pull/148) ([macro1](https://github.com/macro1))
- Fix primary key handling when primary key is a `ForeignKey` [\#145](https://github.com/jazzband/django-simple-history/pull/145) ([macro1](https://github.com/macro1))
- Update Documentation [\#144](https://github.com/jazzband/django-simple-history/pull/144) ([macro1](https://github.com/macro1))

## [1.5.3](https://github.com/jazzband/django-simple-history/tree/1.5.3) (2014-11-19)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.5.2...1.5.3)

**Closed issues:**

- Django 1.7 migration problem with Meta.order\_with\_respect\_to [\#140](https://github.com/jazzband/django-simple-history/issues/140)
- Problems setting up on existing project [\#138](https://github.com/jazzband/django-simple-history/issues/138)
- Django 1.8 Deprecation of Options.module\_name [\#130](https://github.com/jazzband/django-simple-history/issues/130)
- Cannot freeze CustomForeignKeyField when creating south migration [\#129](https://github.com/jazzband/django-simple-history/issues/129)

**Merged pull requests:**

- Fix \#140 - Convert OrderWrt to IntegerField [\#142](https://github.com/jazzband/django-simple-history/pull/142) ([jwhitlock](https://github.com/jwhitlock))
- Fix deprecation error for Django 1.8 [\#137](https://github.com/jazzband/django-simple-history/pull/137) ([jpulec](https://github.com/jpulec))
- Tox fixes [\#136](https://github.com/jazzband/django-simple-history/pull/136) ([jwhitlock](https://github.com/jwhitlock))
- Allow overriding records manager class in register [\#135](https://github.com/jazzband/django-simple-history/pull/135) ([jwhitlock](https://github.com/jwhitlock))
- Some cleanup [\#134](https://github.com/jazzband/django-simple-history/pull/134) ([macro1](https://github.com/macro1))
- \[WIP\] Cleanup test matrix [\#133](https://github.com/jazzband/django-simple-history/pull/133) ([macro1](https://github.com/macro1))
- Fix compatability for south [\#132](https://github.com/jazzband/django-simple-history/pull/132) ([macro1](https://github.com/macro1))
- More fixes for `CustomForeignKey` [\#128](https://github.com/jazzband/django-simple-history/pull/128) ([macro1](https://github.com/macro1))

## [1.5.2](https://github.com/jazzband/django-simple-history/tree/1.5.2) (2014-10-16)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.5.1...1.5.2)

## [1.5.1](https://github.com/jazzband/django-simple-history/tree/1.5.1) (2014-10-14)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.5.0...1.5.1)

**Implemented enhancements:**

- HistoricalRecord on abstract parent model class doesn't work [\#63](https://github.com/jazzband/django-simple-history/issues/63)

**Fixed bugs:**

- Historical model doesn't include fields inherited from superclass [\#87](https://github.com/jazzband/django-simple-history/issues/87)

**Closed issues:**

- query history records about distinct\(\)? [\#127](https://github.com/jazzband/django-simple-history/issues/127)
- Issue with CustomForeignKey - 1.5.0 [\#124](https://github.com/jazzband/django-simple-history/issues/124)
- MongoDB \(django-nonrel\) support? [\#123](https://github.com/jazzband/django-simple-history/issues/123)
- Models with the same model name in various applications causes error [\#121](https://github.com/jazzband/django-simple-history/issues/121)
- Historical a model with foreign key that has been used the history funciton [\#120](https://github.com/jazzband/django-simple-history/issues/120)
- Enable/disable of django-simple-history [\#119](https://github.com/jazzband/django-simple-history/issues/119)
- Templates directory missing after pip install [\#117](https://github.com/jazzband/django-simple-history/issues/117)
- history\_user error during usage of simple\_history.middleware.HistoryRequestMiddleware [\#114](https://github.com/jazzband/django-simple-history/issues/114)
- most\_recent, as\_of return \<Model\>, not \<HistoricalModel\> [\#113](https://github.com/jazzband/django-simple-history/issues/113)
- New version release? [\#110](https://github.com/jazzband/django-simple-history/issues/110)
- problem with southmigration [\#107](https://github.com/jazzband/django-simple-history/issues/107)
- Django 1.7 & pytest-django break simplehistory models [\#104](https://github.com/jazzband/django-simple-history/issues/104)

**Merged pull requests:**

- Make `CustomForeignKeyField` importable, fix migrations with `CustomForeignKeyField` [\#126](https://github.com/jazzband/django-simple-history/pull/126) ([macro1](https://github.com/macro1))
- Added support for django-nonrel string AutoField primary key. [\#125](https://github.com/jazzband/django-simple-history/pull/125) ([DAV3HIT3](https://github.com/DAV3HIT3))
- Fix related accessor conflict on auth user model [\#122](https://github.com/jazzband/django-simple-history/pull/122) ([macro1](https://github.com/macro1))
- Update models.py [\#115](https://github.com/jazzband/django-simple-history/pull/115) ([RossLote](https://github.com/RossLote))
- Allow non-default admin instances [\#111](https://github.com/jazzband/django-simple-history/pull/111) ([macro1](https://github.com/macro1))

## [1.5.0](https://github.com/jazzband/django-simple-history/tree/1.5.0) (2014-08-17)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.4.0...1.5.0)

**Implemented enhancements:**

- The as\_of method should also work without an instance [\#53](https://github.com/jazzband/django-simple-history/issues/53)
- Add option for setting `history_user` automatically. [\#25](https://github.com/jazzband/django-simple-history/issues/25)

**Closed issues:**

- NoReverseMatch {{ action.revert\_url }} [\#92](https://github.com/jazzband/django-simple-history/issues/92)
- Add test for required \_history\_user setter [\#50](https://github.com/jazzband/django-simple-history/issues/50)

**Merged pull requests:**

- Fix bug with related [\#109](https://github.com/jazzband/django-simple-history/pull/109) ([treyhunner](https://github.com/treyhunner))
- Set history\_user automatically using middleware [\#108](https://github.com/jazzband/django-simple-history/pull/108) ([macro1](https://github.com/macro1))
- 'as\_of' for models [\#106](https://github.com/jazzband/django-simple-history/pull/106) ([macro1](https://github.com/macro1))

## [1.4.0](https://github.com/jazzband/django-simple-history/tree/1.4.0) (2014-06-30)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.3.0...1.4.0)

**Implemented enhancements:**

- Make django-simple-history compatible with Django 1.7 [\#82](https://github.com/jazzband/django-simple-history/pull/82) ([treyhunner](https://github.com/treyhunner))
- Added the ability to set a custom history\_date. [\#75](https://github.com/jazzband/django-simple-history/pull/75) ([Dunedan](https://github.com/Dunedan))

**Fixed bugs:**

- No history found in admin when underscore in models primary key [\#81](https://github.com/jazzband/django-simple-history/issues/81)
- Problem with unicode verbose\_names :\( [\#76](https://github.com/jazzband/django-simple-history/issues/76)
- Getting error when trying to view a models history [\#65](https://github.com/jazzband/django-simple-history/issues/65)
- Does not work if you defined models in a file other than models.py, and imported in models/\_\_init\_\_.py [\#64](https://github.com/jazzband/django-simple-history/issues/64)
- `save_without_historical_record` doesn't work for manually registered models [\#59](https://github.com/jazzband/django-simple-history/issues/59)
- Historical record model doesn't work with StatusField from django-model-utils [\#51](https://github.com/jazzband/django-simple-history/issues/51)
- "Changed by" displays None when change occurs outside of admin [\#43](https://github.com/jazzband/django-simple-history/issues/43)
- Fix failing tests against Django trunk [\#22](https://github.com/jazzband/django-simple-history/issues/22)
- Fix foreign key field with custom name [\#13](https://github.com/jazzband/django-simple-history/issues/13)

**Closed issues:**

- History diff [\#83](https://github.com/jazzband/django-simple-history/issues/83)
- add "add to installed apps" [\#69](https://github.com/jazzband/django-simple-history/issues/69)
- Is there a way to see the old copy instead of the latest one [\#58](https://github.com/jazzband/django-simple-history/issues/58)
- Is there a way to reference a Historical Entry using models.ForeignKey? [\#57](https://github.com/jazzband/django-simple-history/issues/57)
- Tracking a Custom User [\#56](https://github.com/jazzband/django-simple-history/issues/56)
- Add screenshots to documentation [\#52](https://github.com/jazzband/django-simple-history/issues/52)
- Foreign keys which aren't integers [\#38](https://github.com/jazzband/django-simple-history/issues/38)
- Rename history\_user to changed\_by [\#14](https://github.com/jazzband/django-simple-history/issues/14)

**Merged pull requests:**

- Create 1.4.0 release of django-simple-history [\#102](https://github.com/jazzband/django-simple-history/pull/102) ([treyhunner](https://github.com/treyhunner))
- Basic code style cleanup [\#101](https://github.com/jazzband/django-simple-history/pull/101) ([treyhunner](https://github.com/treyhunner))
- Add tests to demonstrate \#43 [\#100](https://github.com/jazzband/django-simple-history/pull/100) ([macro1](https://github.com/macro1))
- Populate history command [\#99](https://github.com/jazzband/django-simple-history/pull/99) ([macro1](https://github.com/macro1))
- Add override for historical model base classes [\#98](https://github.com/jazzband/django-simple-history/pull/98) ([macro1](https://github.com/macro1))
- Fix Python 3.2 tests [\#97](https://github.com/jazzband/django-simple-history/pull/97) ([macro1](https://github.com/macro1))
- Correctly handle admin URL's with escaped pk's [\#96](https://github.com/jazzband/django-simple-history/pull/96) ([macro1](https://github.com/macro1))
- Set authentication middleware for test runner [\#95](https://github.com/jazzband/django-simple-history/pull/95) ([macro1](https://github.com/macro1))
- Updating usage docs [\#94](https://github.com/jazzband/django-simple-history/pull/94) ([mauricioabreu](https://github.com/mauricioabreu))
- New tests for get\_model for models that register themselves into other apps. [\#91](https://github.com/jazzband/django-simple-history/pull/91) ([johnistan](https://github.com/johnistan))
- Revert the addition of my nickname to AUTHORS.rst, as my realname is already included [\#90](https://github.com/jazzband/django-simple-history/pull/90) ([Dunedan](https://github.com/Dunedan))
- Added screenshots to documentation \(issue \#52\) [\#89](https://github.com/jazzband/django-simple-history/pull/89) ([bjdixon](https://github.com/bjdixon))
- Fix bug when verbose\_name of model is unicode [\#80](https://github.com/jazzband/django-simple-history/pull/80) ([treyhunner](https://github.com/treyhunner))
- Cross-link recording user and admin docs [\#79](https://github.com/jazzband/django-simple-history/pull/79) ([treyhunner](https://github.com/treyhunner))
- Update advanced.rst [\#78](https://github.com/jazzband/django-simple-history/pull/78) ([dmckean](https://github.com/dmckean))
- Add a Bitdeli Badge to README [\#71](https://github.com/jazzband/django-simple-history/pull/71) ([bitdeli-chef](https://github.com/bitdeli-chef))
- Iss59 [\#70](https://github.com/jazzband/django-simple-history/pull/70) ([matklad](https://github.com/matklad))
- Update usage.rst [\#66](https://github.com/jazzband/django-simple-history/pull/66) ([vnagendra](https://github.com/vnagendra))
- verbose\_name handling for the HistoricalRecord model [\#62](https://github.com/jazzband/django-simple-history/pull/62) ([foobacca](https://github.com/foobacca))
- Fix disappearing reverse relationship \(ie modelname\_set \) from model with history [\#61](https://github.com/jazzband/django-simple-history/pull/61) ([foobacca](https://github.com/foobacca))
- Fixes bug with foreign keys to one-to-one fields [\#55](https://github.com/jazzband/django-simple-history/pull/55) ([daniell](https://github.com/daniell))
- Check code style in tests [\#49](https://github.com/jazzband/django-simple-history/pull/49) ([treyhunner](https://github.com/treyhunner))
- add tests + foreign-key fix \(issue \#38\) [\#41](https://github.com/jazzband/django-simple-history/pull/41) ([dnozay](https://github.com/dnozay))

## [1.3.0](https://github.com/jazzband/django-simple-history/tree/1.3.0) (2013-05-18)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.2.3...1.3.0)

**Fixed bugs:**

- Error due to issue \#7 fix [\#42](https://github.com/jazzband/django-simple-history/issues/42)
- Fix `save_without_historical_record` when `save` raises error [\#12](https://github.com/jazzband/django-simple-history/issues/12)
- history property not picked when model class is in a models directory [\#7](https://github.com/jazzband/django-simple-history/issues/7)

**Closed issues:**

- custom user model not working with SimpleHIstoryAdmin [\#46](https://github.com/jazzband/django-simple-history/issues/46)
- more examples? [\#45](https://github.com/jazzband/django-simple-history/issues/45)
- Add documentation [\#19](https://github.com/jazzband/django-simple-history/issues/19)

**Merged pull requests:**

- Custom user support [\#48](https://github.com/jazzband/django-simple-history/pull/48) ([matklad](https://github.com/matklad))
- fix code for app\_label \(issue \#42\) [\#47](https://github.com/jazzband/django-simple-history/pull/47) ([dnozay](https://github.com/dnozay))
- Python 3.3 compatibility [\#44](https://github.com/jazzband/django-simple-history/pull/44) ([matklad](https://github.com/matklad))
- Sphinx docs [\#40](https://github.com/jazzband/django-simple-history/pull/40) ([treyhunner](https://github.com/treyhunner))
- Allow Django 1.5 custom users [\#39](https://github.com/jazzband/django-simple-history/pull/39) ([jfyne](https://github.com/jfyne))
- allow history table to be formatted correctly when used with bootstrap [\#36](https://github.com/jazzband/django-simple-history/pull/36) ([dnozay](https://github.com/dnozay))
- fix + tests for issue \#12 [\#35](https://github.com/jazzband/django-simple-history/pull/35) ([dnozay](https://github.com/dnozay))
- Add support for model packages [\#34](https://github.com/jazzband/django-simple-history/pull/34) ([treyhunner](https://github.com/treyhunner))
- some doc for enabling custom admin view [\#32](https://github.com/jazzband/django-simple-history/pull/32) ([dnozay](https://github.com/dnozay))

## [1.2.3](https://github.com/jazzband/django-simple-history/tree/1.2.3) (2013-04-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.2.2...1.2.3)

**Fixed bugs:**

- templates missing from pypi packages [\#27](https://github.com/jazzband/django-simple-history/issues/27)

**Merged pull requests:**

- Package fix [\#31](https://github.com/jazzband/django-simple-history/pull/31) ([treyhunner](https://github.com/treyhunner))

## [1.2.2](https://github.com/jazzband/django-simple-history/tree/1.2.2) (2013-04-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.2.1...1.2.2)

**Closed issues:**

- tag 1.2.1 is missing [\#28](https://github.com/jazzband/django-simple-history/issues/28)

## [1.2.1](https://github.com/jazzband/django-simple-history/tree/1.2.1) (2013-04-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.2.0...1.2.1)

## [1.2.0](https://github.com/jazzband/django-simple-history/tree/1.2.0) (2013-04-22)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.1.3...1.2.0)

**Fixed bugs:**

- Fix broken tox tests with Python 2.6 [\#23](https://github.com/jazzband/django-simple-history/issues/23)
- save on django admin tool is not saving the history [\#11](https://github.com/jazzband/django-simple-history/issues/11)

**Closed issues:**

- Add test for saving in admin interface [\#21](https://github.com/jazzband/django-simple-history/issues/21)
- Add tests for historical model form [\#20](https://github.com/jazzband/django-simple-history/issues/20)
- Add tests for FileField and ImageField [\#18](https://github.com/jazzband/django-simple-history/issues/18)
- Add test for save with `raw` keyword argument [\#15](https://github.com/jazzband/django-simple-history/issues/15)
- TypeError 'company\_id' is an invalid keyword argument for this function [\#1](https://github.com/jazzband/django-simple-history/issues/1)

**Merged pull requests:**

- Improve test coverage and fix some model manager bugs [\#24](https://github.com/jazzband/django-simple-history/pull/24) ([treyhunner](https://github.com/treyhunner))
- Add more tests [\#10](https://github.com/jazzband/django-simple-history/pull/10) ([treyhunner](https://github.com/treyhunner))
- Add tests [\#8](https://github.com/jazzband/django-simple-history/pull/8) ([treyhunner](https://github.com/treyhunner))
- Remove unused and pointless lines [\#6](https://github.com/jazzband/django-simple-history/pull/6) ([jsanchezpando](https://github.com/jsanchezpando))
- Copy path to history database, do not history files content [\#5](https://github.com/jazzband/django-simple-history/pull/5) ([jsanchezpando](https://github.com/jsanchezpando))

## [1.1.3](https://github.com/jazzband/django-simple-history/tree/1.1.3) (2012-08-23)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.1.2...1.1.3)

## [1.1.2](https://github.com/jazzband/django-simple-history/tree/1.1.2) (2012-08-21)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.1.1...1.1.2)

## [1.1.1](https://github.com/jazzband/django-simple-history/tree/1.1.1) (2012-02-26)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.1.0...1.1.1)

## [1.1.0](https://github.com/jazzband/django-simple-history/tree/1.1.0) (2011-10-13)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/1.0...1.1.0)

## [1.0](https://github.com/jazzband/django-simple-history/tree/1.0) (2010-12-02)

[Full Changelog](https://github.com/jazzband/django-simple-history/compare/05b329affe89134d93200b03652d14b5e43a618a...1.0)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
