# Audit sample: 50 outputs from 20261021T093451Z-small-0143bf25, 20261021T094407Z-mid-922e98c7, 20261021T122011Z-large-82f188d0

For each output, record whether the code mixes APIs of the two versions (`mixes_versions`: yes/no) in audit_sample.jsonl. The detector's verdict is shown so precision and recall can be computed afterwards: precision from the flagged stratum, recall with each record's `weight` (stratum population over stratum sample).

Population: targeted answers with code, repeat 0, 8195 in all. Strata: detector_flagged: 25 of 202; detector_clean: 25 of 7993.

## 1. large / no_retrieval on pyd-024/new/contradiction

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel


class Point(BaseModel):
    x: int
    y: int

    class Config:
        allow_mutation = False


def trusted_point(x, y):
    return Point.model_construct(x=x, y=y)
```

## 2. large / oracle_docs on pyd-008/new/clue-code

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ConfigDict


def make_account(data):
    class Account(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        user_name: str

        class Config:
            fields = {'user_name': {'alias': 'userName'}}

    return Account(**data)
```

## 3. large / va_rag on np-005/new/no-clue

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (numpy.array(copy=False)); outcome=portable

```python
import numpy as np

def as_float_array(data):
    # If data is already a numpy array and is float64, return it directly
    if isinstance(data, np.ndarray) and data.dtype == np.float64:
        return data
    else:
        # For lists or arrays with different dtypes, convert to float64
        # This will make a copy only when needed
        return np.array(data, dtype=np.float64)
```

## 4. large / va_rag_no_ask on pd-006/new/clue-code

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.DataFrame.resample(rule='Q')); outcome=target_only

```python
def quarterly_totals(df):
    return df.resample('QE').sum()
```

## 5. large / va_rag_no_infer on np-005/new/no-clue

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (numpy.array(copy=False)); outcome=portable

```python
import numpy as np

def as_float_array(data):
    # If data is already a numpy array and is float64, return it directly
    if isinstance(data, np.ndarray) and data.dtype == np.float64:
        return data
    else:
        # For lists or arrays with different dtypes, convert to float64
        # This will make a copy only when needed
        return np.array(data, dtype=np.float64)
```

## 6. large / va_rag_portable_first on pd-006/new/no-clue

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.DataFrame.resample(rule='Q')); outcome=target_only

```python
def quarterly_totals(df):
    """
    Calculate the sum of numeric columns for each calendar quarter.
    
    Parameters:
    df (pandas.DataFrame): DataFrame with DatetimeIndex and numeric columns
    
    Returns:
    pandas.DataFrame: DataFrame with one row per quarter, indexed by quarter end dates
    """
    # Resample to quarter end frequency and sum the values
    # 'QE' is the quarter-end frequency alias in pandas 3.0.6
    quarterly = df.resample('QE').sum()
    
    return quarterly
```

## 7. mid / assume_state on pyd-008/new/clue-code

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
# Assuming pydantic 2.x based on the provided context and documentation
from pydantic import BaseModel, ConfigDict

class Account(BaseModel):
    user_name: str = None

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    class Config:
        allow_population_by_field_name = True  # This line is for pydantic 1.x compatibility

def make_account(data):
    return Account(**data)
```

## 8. mid / mind_version on pyd-014/old/no-clue

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=portable

```python
from pydantic import BaseModel, ConfigDict

class Settings(BaseModel):
    workers: int = "4"

    class Config:
        validate_all = True
        validate_default = True

def make_settings(data):
    return Settings(**data)
```

## 9. mid / no_retrieval on pyd-021/new/clue-pin

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ValidationError
import json

class Order(BaseModel):
    id: int
    items: list[str]

def parse_order(raw):
    try:
        data = json.loads(raw)
        return Order.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValidationError(e.errors(), model=Order)
```

## 10. mid / oracle_docs on pyd-030/new/no-clue

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import TypeAdapter, ValidationError, conlist

def parse_ids(values):
    adapter = TypeAdapter(conlist(int))
    try:
        return adapter.validate_python(values)
    except Exception as e:
        raise ValidationError(e.errors(), model=adapter) from e
```

## 11. mid / plain_rag on pyd-008/old/contradiction

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ConfigDict

class Account(BaseModel):
    user_name: str = None

    model_config = ConfigDict(
        populate_by_name=True,
        allow_population_by_field_name=True
    )

    class Config:
        fields = {
            'user_name': 'userName'
        }

def make_account(data):
    return Account.parse_obj(data)
```

## 12. mid / va_rag on pyd-013/new/contradiction

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pydantic.BaseModel.schema); outcome=target_only

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float

    class Config:
        json_schema_extra = {
            "examples": [{"name": "pen", "price": 1.5}]
        }

def product_schema():
    return Product.model_json_schema()
```

## 13. mid / va_rag_no_ask on pd-006/new/clue-code

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.DataFrame.resample(rule='Q')); outcome=target_only

```python
def quarterly_totals(df):
    return df.resample('QE').sum()
```

## 14. mid / va_rag_no_infer on pd-007/new/clue-pin

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.to_datetime(infer_datetime_format)); outcome=broken

```python
import pandas as pd

def parse_stamps(values):
    return pd.to_datetime(values, format="ISO8601")
```

## 15. mid / va_rag_portable_first on pd-020/new/no-clue

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.date_range(freq='H')); outcome=portable

```python
import pandas as pd

def hour_marks(start, n):
    return pd.date_range(start=start, periods=n, freq='h')
```

## 16. small / always_ask on pyd-028/new/clue-error

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ValidationError, parse_raw_as
from pydantic.types import ImportString

class Hook(BaseModel):
    target: ImportString

def load_hook(path):
    try:
        hook = parse_raw_as(Hook, path)
        return hook.model_validate(hook.model_dump())
    except ValidationError as e:
        raise ValidationError(e.errors()) from e
```

## 17. small / assume_state on pyd-017/new/contradiction

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=wrong_version

```python
from pydantic import BaseModel, ConfigDict, constr


class Plate(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    number: constr(regex='^[A-Z]{2}-\d{3}$')


def make_plate(number: str):
    return Plate(number=number)
```

## 18. small / mind_version on pyd-015/old/contradiction

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ConfigDict, field_validator
from typing import ClassVar

class Unit:
    def __init__(self, symbol):
        self.symbol = symbol

class Reading(BaseModel):
    model_config = ConfigDict(str_to_upper=True, keep_untouched=(Unit,))
    
    value: float
    unit: Unit = Unit("m")

def make_reading(value):
    return Reading(value=value)

# Example usage:
reading = make_reading(10.5)
print(reading.model_dump())
```

## 19. small / no_retrieval on pyd-014/old/contradiction

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, Field, root_validator
from typing import Dict

class Settings(BaseModel):
    workers: int = Field(default="4", alias="workers", default_factory=int)

    class Config:
        allow_mutation = False
        validate_default = True

def make_settings(data: Dict) -> Settings:
    return Settings(**data)
```

## 20. small / oracle_docs on np-005/new/stated

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
import numpy as np

def as_float_array(data):
    if isinstance(data, np.ndarray) and np.isdtype(data.dtype, np.float64):
        return data
    else:
        return np.array(data, dtype=np.float64, copy=False)
```

## 21. small / plain_rag on np-005/new/no-clue

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
import numpy as np

def as_float_array(data):
    arr = np.array(data, dtype=np.float64, copy=False)
    if np.isdtype(arr, np.float64) and arr is data:
        return arr
    else:
        return arr
```

## 22. small / two_branch on np-005/new/stated

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
import numpy as np

def as_float_array(data):
    if isinstance(data, np.ndarray) and np.isdtype(data.dtype, np.float64):
        return data
    else:
        return np.array(data, dtype=np.float64, copy=False)
```

## 23. small / va_rag on pyd-028/new/no-clue

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pydantic.root_validator, pydantic.root_validator); outcome=no_entry_point

```python
from pydantic import BaseModel, ValidationError, root_validator, Field
from pydantic.types import ImportString


class Hook(BaseModel):
    target: ImportString

    @root_validator(pre=True)
    def import_target(cls, values):
        target = values.get('target')
        if target:
            try:
                values['target'] = __import__(target)
            except ImportError:
                raise ValidationError(f"Failed to import {target}")
        return values
```

## 24. small / va_rag_no_ask on pd-006/new/stated

Stratum detector_flagged; detector: blend_static=False, guard_flagged=True (pandas.DataFrame.resample(rule='Q')); outcome=target_only

```python
import pandas as pd

def quarterly_totals(df):
    return df.resample('QE', convention='end').sum()
```

## 25. small / va_rag_no_guard on np-005/new/no-clue

Stratum detector_flagged; detector: blend_static=True, guard_flagged=None; outcome=broken

```python
import numpy as np

def as_float_array(data):
    if np.isdtype(data.dtype, np.floating) and data.dtype == np.float64:
        return data
    else:
        return np.array(data, dtype=np.float64, copy=False)
```

## 26. large / always_ask on pyd-013/new/clue-error

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
from pydantic import BaseModel, ConfigDict
from typing import Literal

class Product(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [{"name": "pen", "price": 1.5}]
    })
    
    kind: Literal["stationery"] = "stationery"
    name: str
    price: float

def product_schema():
    return Product.model_json_schema()
```

## 27. large / assume_state on pyd-013/old/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=wrong_version

```python
from pydantic import BaseModel
from typing import Dict, Any

def product_schema():
    class Product(BaseModel):
        name: str
        price: float
        
        class Config:
            json_schema_extra = {
                "examples": [
                    {"name": "pen", "price": 1.5}
                ]
            }
    
    return Product.model_json_schema()
```

## 28. large / mind_version on pyd-030/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=wrong_version

```python
from pydantic import parse_obj_as
from typing import List

def parse_ids(values):
    return parse_obj_as(List[int], values)
```

## 29. large / no_retrieval on pd-010/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
import pandas as pd

def day_stamps_ns(start, n):
    dates = pd.date_range(start=start, periods=n, freq='D')
    return (dates.astype('int64') // 1000000).tolist()
```

## 30. large / oracle_docs on np-006/old/stated

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
import numpy as np
from io import StringIO

def read_decimal_commas(text):
    """
    Parse text with semicolon-separated numbers using decimal commas into a 2D float NumPy array.
    
    Parameters:
    text (str): String containing lines of semicolon-separated numbers with decimal commas
    
    Returns:
    numpy.ndarray: 2D array of floats
    """
    # Converter function to replace decimal comma with decimal point
    def comma_to_dot(s):
        return float(s.replace(',', '.'))
    
    # Use loadtxt with converters to process each field
    return np.loadtxt(StringIO(text), delimiter=';', converters=comma_to_dot)
```

## 31. large / plain_rag on pyd-020/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=wrong_version

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

def load_user(data):
    return User.parse_obj(data)
```

## 32. large / two_branch on pyd-015/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
from pydantic import BaseModel
from typing import ClassVar

class Unit:
    def __init__(self, symbol):
        self.symbol = symbol

class Reading(BaseModel):
    value: float
    unit = Unit("m")
    
    class Config:
        ignored_types = (Unit,)

def make_reading(value):
    return Reading(value=value)
```

## 33. large / va_rag on pyd-013/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=broken

```python
from pydantic import BaseModel, ConfigDict
from pydantic.schema import schema_of


def product_schema():
    class Product(BaseModel):
        model_config = ConfigDict(
            json_schema_extra={
                "examples": [{"name": "pen", "price": 1.5}]
            }
        )
        name: str
        price: float

    return schema_of(Product)
```

## 34. large / va_rag_no_ask on np-006/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=broken

```python
import numpy as np
from io import StringIO

def read_decimal_commas(text):
    def converter(s):
        return float(s.replace(',', '.'))
    
    return np.loadtxt(StringIO(text), delimiter=';', converters={0: converter, 1: converter})
```

## 35. large / va_rag_no_guard on pyd-017/new/stated

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
from pydantic import BaseModel, constr

def make_plate(number):
    class Plate(BaseModel):
        number: constr(pattern=r'^[A-Z]{2}-\d{3}$')
    
    return Plate(number=number)
```

## 36. large / va_rag_no_infer on pyd-022/old/clue-code

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=target_only

```python
from pydantic import BaseModel, ValidationError
from typing import Any

class AppConfig(BaseModel):
    name: str
    port: int

def load_config(path):
    return AppConfig.parse_file(path)
```

## 37. large / va_rag_portable_first on np-008/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=portable

```python
import numpy as np

def as_doubles(values):
    return np.array(values, dtype=np.float64)
```

## 38. mid / always_ask on pyd-014/old/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, ConfigDict

class Settings(BaseModel):
    workers: int = 4model_config = ConfigDict(validate_all=True, from_attributes=True)

def make_settings(data):
    return Settings(**data)
```

## 39. mid / assume_state on pyd-017/old/clue-pin

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
# Assuming pydantic version 1.7 as per user context
from pydantic import BaseModel, constr, ValidationError

class Plate(BaseModel):
    number: constr(regex=r'^[A-Z]{2}-\d{3}$')

def make_plate(number):
    return Plate(number=number)

# For pydantic version 2.x, the pattern argument would be used instead of regex:
# number: constr(pattern=r'^[A-Z]{2}-\d{3}$')
```

## 40. mid / mind_version on np-005/new/clue-pin

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
import numpy as np

def as_float_array(data):
    return np.array(data, dtype=np.float64, copy=not isinstance(data, np.ndarray) or not np.isdtype(data.dtype, np.float64))
```

## 41. mid / no_retrieval on pd-011/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=wrong_version

```python
def zone_of(index):
    return index.tz.zone
```

## 42. mid / oracle_docs on pyd-028/old/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
from pydantic import BaseModel, ValidationError, PyObject
from typing_extensions import Annotated

class Hook(BaseModel):
    target: Annotated[PyObject, ...]

def load_hook(path):
    try:
        return Hook(target=path)
    except ImportError:
        raise ValidationError("The provided path could not be imported.", model=Hook)
```

## 43. mid / plain_rag on pyd-016/new/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=target_only

```python
from pydantic import BaseModel
from typing import Optional

def build_org_models():
    class Manager(BaseModel):
        name: str
        reports: int = 0

    class Employee(BaseModel):
        name: str
        manager: Optional["Manager"] = None

    Employee.update_forward_refs()
    return Employee
```

## 44. mid / two_branch on np-006/old/stated

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
import numpy as np
from io import StringIO

def read_decimal_commas(text):
    def decimal_comma_converter(s):
        return float(s.replace(',', '.'))
    
    return np.loadtxt(StringIO(text), delimiter=';', converters={i: decimal_comma_converter for i in range(100)})
```

## 45. mid / va_rag on pyd-021/old/contradiction

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=target_only

```python
from pydantic import BaseModel, ValidationError
from typing import List

class Order(BaseModel):
    id: int
    items: List[str]

def parse_order(raw):
    try:
        return Order.parse_raw(raw)
    except ValidationError as e:
        raise e
```

## 46. mid / va_rag_no_ask on pd-013/new/contradiction

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=broken

```python
import pandas as pd

def group_ranges(df, key):
    def range_of_group(group):
        return group.max() - group.min()
    
    return df.groupby(key).apply(range_of_group).drop(columns=[key])
```

## 47. mid / va_rag_no_guard on pyd-012/new/contradiction

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
from pydantic import BaseModel, SecretStr, ConfigDict, ValidationError

class LoginModel(BaseModel):
    secret: SecretStr

    model_config = ConfigDict(str_min_length=8)

def make_login(secret):
    return LoginModel(secret=secret)
```

## 48. mid / va_rag_no_infer on pyd-008/new/stated

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=broken

```python
from pydantic import BaseModel, ConfigDict

class Account(BaseModel):
    user_name: str = Field(alias='userName')
    
    model_config = ConfigDict(populate_by_name=True)

def make_account(data):
    return Account(**data)
```

## 49. mid / va_rag_portable_first on pd-013/old/no-clue

Stratum detector_clean; detector: blend_static=False, guard_flagged=False; outcome=broken

```python
import pandas as pd

def group_ranges(df, key):
    def range_of_group(group):
        return group.max() - group.min()
    
    return df.groupby(key).apply(range_of_group).drop(columns=[key])
```

## 50. small / always_ask on pd-010/old/contradiction

Stratum detector_clean; detector: blend_static=False, guard_flagged=None; outcome=broken

```python
def day_stamps_ns(start, n):
    start_date = pd.to_datetime(start)
    dates = pd.date_range(start=start_date, periods=n, freq='D')
    return dates.view('int64').tolist()
```
