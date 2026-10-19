# Audit sample: 20261019T122241Z-primary-d482d646 (50 outputs)

For each output, record whether the code mixes APIs of the two versions (`mixes_versions`: yes/no) in audit_sample.jsonl. The detector's verdict is shown so precision and recall can be computed afterwards.

## 1. always_ask on pyd-004/new/stated

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, model_validator

class RangeModel(BaseModel):
    lo: int
    hi: int

    @model_validator(mode='after')
    def check_range(cls, values):
        if values['hi'] < values['lo']:
            raise ValueError('hi must be greater than or equal to lo')
        return values
```

## 2. assume_state on pd-001/old/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import pandas as pd

def format_cells(df, fmt):
    return df.applymap(lambda x: fmt.format(x))
```

## 3. mind_version on np-001/old/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 4. no_retrieval on np-002/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import numpy as np

def code_grid(values):
    unique_values, inverse_indices = np.unique(values, return_inverse=True)
    counts = np.bincount(inverse_indices)
    return inverse_indices.reshape(values.shape), counts
```

## 5. oracle_docs on pyd-007/old/stated

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)
```

## 6. plain_rag on np-001/new/clue-code

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 7. two_branch on np-003/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
import numpy as np

def lower_median(values):
    """
    Calculate the lower median of a sequence of numbers as a float.
    
    Parameters:
    values (array-like): A sequence of numbers.
    
    Returns:
    float: The lower median of the sequence.
    """
    values = np.array(values)
    if np.isnan(values).any():
        values = np.nan_to_num(values, nan=np.inf)
    return np.percentile(values, 50, interpolation='lower')
```

## 8. va_rag on pd-001/old/no-clue

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import pandas as pd

def format_cells(df, fmt):
    return df.applymap(lambda x: fmt.format(x))
```

## 9. va_rag_no_ask on pyd-002/new/stated

Detector: blend_static=False, guard_flagged=True, outcome=target_only

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

def user_from_orm(obj):
    return User.model_validate(obj, from_attributes=True)
```

## 10. va_rag_no_guard on pd-004/old/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
import pandas as pd

def to_epoch_ns(values):
    dt_series = pd.to_datetime(values)
    epoch_ns = (dt_series - pd.Timestamp('1970-01-01')) * 1e9
    return epoch_ns.astype(int).to_list()
```

## 11. va_rag_no_infer on np-001/old/stated

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 12. always_ask on np-001/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    """
    Returns the area under the curve sampled as values `y` at positions `x`, computed with NumPy's built-in trapezoidal-rule integration function. Returns a plain float.
    """
    return np.trapezoid(y, x).item()
```

## 13. assume_state on np-001/old/stated

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 14. mind_version on pyd-001/new/stated

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field, model_validator

class Model(BaseModel):
    code: str = Field(..., pattern=r'^[A-Z]{3}-\d{4}$')

    @model_validator(mode='after')
    def check_code_format(cls, model):
        return model
```

## 15. no_retrieval on pyd-004/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, validator

class RangeModel(BaseModel):
    lo: int
    hi: int

    @validator('*', pre=True)
    def check_order(cls, v, values, field):
        if field.name == 'hi' and v < values.get('lo'):
            raise ValueError('hi must be greater than or equal to lo')
        return v
```

## 16. oracle_docs on pyd-005/old/clue-error

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.dict()
```

## 17. plain_rag on pyd-005/old/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.dict()
```

## 18. two_branch on pd-002/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import pandas as pd

def month_ends(start, n):
    start_date = pd.to_datetime(start)
    end_date = start_date + pd.DateOffset(months=n)
    return pd.date_range(start=start_date, end=end_date, freq='M')[-n:]
```

## 19. va_rag on np-003/new/clue-pin

Detector: blend_static=False, guard_flagged=False, outcome=broken

```python
import numpy as np

def lower_median(values):
    return np.percentile(values, 50, method='lower')
```

## 20. va_rag_no_ask on pd-002/new/stated

Detector: blend_static=False, guard_flagged=True, outcome=broken

```python
import pandas as pd

def month_ends(start, n):
    start_date = pd.to_datetime(start)
    end_date = start_date + pd.DateOffset(months=n)
    return pd.date_range(start=start_date, end=end_date, freq='ME')[-1::-1]
```

## 21. va_rag_no_guard on pd-001/old/stated

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import pandas as pd

def format_cells(df, fmt):
    return df.applymap(lambda x: fmt.format(x))
```

## 22. va_rag_no_infer on np-001/old/clue-pin

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 23. always_ask on pyd-006/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace-only')
        return v

def make_user(name: str) -> User:
    return User(name=name)
```

## 24. assume_state on pyd-006/old/clue-code

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, validator

class User(BaseModel):
    name: str

    @validator('name', pre=True, always=True)
    def check_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace-only')
        return v
```

## 25. mind_version on pd-004/old/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
import pandas as pd

def to_epoch_ns(values):
    dt_series = pd.to_datetime(values)
    epoch_ns = (dt_series - pd.Timestamp('1970-01-01')) * 1e9
    return epoch_ns.astype(int).tolist()
```

## 26. no_retrieval on np-002/old/stated

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def code_grid(values):
    unique_values, inverse_indices = np.unique(values, return_inverse=True)
    counts = np.bincount(inverse_indices)
    return inverse_indices.reshape(values.shape), counts
```

## 27. oracle_docs on pyd-006/new/clue-error

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace-only')
        return v
```

## 28. plain_rag on pyd-005/old/clue-error

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.dict()
```

## 29. two_branch on np-002/new/clue-code

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import numpy as np

def code_grid(values):
    unique_values, inverse = np.unique(values, return_inverse=True)
    counts = np.bincount(inverse)
    return inverse.reshape(values.shape), counts
```

## 30. va_rag on pd-001/old/clue-pin

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import pandas as pd

def format_cells(df, fmt):
    return df.applymap(lambda x: fmt.format(x))
```

## 31. va_rag_no_ask on pyd-006/new/stated

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace-only')
        return v

def make_user(name: str) -> User:
    return User(name=name)
```

## 32. va_rag_no_guard on np-001/new/stated

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapezoid(y, x)
```

## 33. va_rag_no_infer on pd-005/new/clue-code

Detector: blend_static=False, guard_flagged=False, outcome=portable

```python
import pandas as pd

def fill_forward(df):
    return df.ffill()
```

## 34. always_ask on np-002/new/stated

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import numpy as np

def code_grid(values):
    unique_values, inverse = np.unique(values, return_inverse=True)
    counts = np.bincount(inverse)
    return inverse.reshape(values.shape), counts
```

## 35. assume_state on pyd-001/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field, validator

class Model(BaseModel):
    code: str = Field(..., regex=r"^[A-Z]{3}-\d{4}$")

    class Config:
        fields = {
            'code': 'code'
        }
```

## 36. mind_version on pyd-005/old/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.dict()
```

## 37. no_retrieval on pyd-007/old/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)
```

## 38. oracle_docs on pyd-002/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

def user_from_orm(obj):
    return User.from_orm(obj)
```

## 39. plain_rag on pd-004/new/clue-code

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
import pandas as pd

def to_epoch_ns(values):
    dt_series = pd.to_datetime(values)
    epoch_ns = dt_series.dt.value.astype('int64') // 10**9
    return epoch_ns.tolist()
```

## 40. two_branch on pd-005/new/no-clue

Detector: blend_static=False, guard_flagged=None, outcome=portable

```python
import pandas as pd
import numpy as np

def fill_forward(df):
    return df.ffill()
```

## 41. va_rag on pd-003/new/stated

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import pandas as pd

def load_orders(path):
    return pd.read_csv(path, parse_dates=['ordered_at'], date_format='%d/%m/%Y')
```

## 42. va_rag_no_ask on pyd-005/new/no-clue

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.model_dump(by_alias=True)
```

## 43. va_rag_no_guard on pyd-007/old/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)
```

## 44. va_rag_no_infer on np-001/new/clue-code

Detector: blend_static=False, guard_flagged=False, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapezoid(y, x)
```

## 45. always_ask on pyd-007/old/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=broken

```python
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)
```

## 46. assume_state on np-002/new/clue-code

Detector: blend_static=False, guard_flagged=None, outcome=portable

```python
import numpy as np

def code_grid(values):
    unique_values, inverse_indices, counts = np.unique(values, return_inverse=True, return_counts=True)
    codes = inverse_indices.reshape(values.shape)
    return codes, counts
```

## 47. mind_version on np-001/old/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import numpy as np

def area_under(y, x):
    return np.trapz(y, x)
```

## 48. no_retrieval on pd-003/old/stated

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
import pandas as pd

def load_orders(path):
    return pd.read_csv(path, parse_dates=['ordered_at'], date_parser=lambda x: pd.to_datetime(x, dayfirst=True))
```

## 49. oracle_docs on pd-001/new/stated

Detector: blend_static=False, guard_flagged=None, outcome=wrong_version

```python
import pandas as pd

def format_cells(df, fmt):
    return df.applymap(fmt.format)
```

## 50. plain_rag on pyd-005/new/clue-pin

Detector: blend_static=False, guard_flagged=None, outcome=target_only

```python
from pydantic import BaseModel

def to_record(model: BaseModel) -> dict:
    return model.model_dump(by_alias=True)
```
