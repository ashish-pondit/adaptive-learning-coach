# Quiz Bank & Teaching Notes for Adaptive Learning Coach

Pre-written quizzes AND teaching notes organized by task ID. Content not found here will be generated dynamically from the learning plan.

---

## Level 0: Prerequisites

### Task 0.1: C# Syntax Basics

#### 📚 Teaching Notes

**Complexity**: SIMPLE (single clear concept, direct Python equivalent)

**Concept Summary**:
```
📚 What is it:
C# is a strongly-typed language with explicit statement endings (semicolons) 
and brace-delimited code blocks. Unlike Python's dynamic typing and indentation,
C# requires type declarations and uses {} for scope.

Why it matters:
Strong typing catches errors at compile-time, not runtime.
Explicit syntax makes code structure visually clear.

✨ Key Insight: "Noisy" syntax = safer code. The extra characters 
   help the compiler (and you) understand intent.
```

**Django/Python Comparison**:
```
🔗 Python vs C# Syntax:

Python:
  x = 5                    # Dynamic typing, no semicolon
  if x > 0:                # Indentation defines block
      print("positive")    # Indented block

C#:
  int x = 5;               // Typed, semicolon ends statement
  if (x > 0)               // Parentheses required
  {                        // Brace starts block
      Console.WriteLine("positive"); // Semicolon required
  }                        // Brace ends block

Key differences:
  • Types: Python infers, C# declares (or uses var)
  • Semicolons: Python none, C# required
  • Blocks: Python indentation, C# braces
  • Parentheses: Python optional in some cases, C# required for conditions

💡 Your Python experience: You know variable assignment.
   C# just adds type declaration before the name.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Entities/User.cs (lines 1-50)
  
Focus on:
  • Line 5-10: Property declarations - see { get; set; } syntax
  • Notice semicolons after each property
  • Notice braces around the class body

🔍 Look for:
  - Where braces start/end the class
  - Semicolons after property declarations
  - Type names before property names (int, string, bool)
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: C# Fundamentals
    https://learn.microsoft.com/en-us/dotnet/csharp/
    
  • Your project: /iam/CLAUDE.md (coding conventions)
```

**Mini-Lecture**: NOT NEEDED (simple topic, summary sufficient)
```
💡 For deeper explanation, user can request "explain more"
```

---

#### 📚 Concept Quiz

```
Q1: In C#, what character ends a statement?
   A) Newline
   B) Semicolon ;
   C) Colon :
   D) Period .

Q2: What is the difference between `var` and explicit types in C#?
   A) `var` creates a dynamic type
   B) `var` is type inference at compile time
   C) `var` is only for local variables
   D) There is no difference

Q3: Why does C# use braces {} for code blocks instead of indentation?
   A) For readability
   B) Historical reasons from C/C++
   C) To support nested blocks clearly
   D) All of the above
```

#### 🔗 Elaboration

```
Q: How is C# syntax different from Python? List 3 key differences.
Q: Why might a Python developer find C# "noisy" at first?
Q: What advantage does explicit typing provide over Python's dynamic typing?
```

#### 🎯 Teach-Back

```
Explain to a Python developer:
- What `var` does in C# and when to use it
- Why statements need semicolons
- How braces define scope
```

---

### Task 0.2: Types & Variables

#### 📚 Teaching Notes

**Complexity**: SIMPLE (direct concepts)

**Concept Summary**:
```
📚 What is it:
C# has built-in types: int (integer), string (text), bool (true/false), 
double (decimal). Variables must be declared with type. Modern C# allows 
nullable reference types with ? suffix (string? = can be null).

Why it matters:
Understanding types prevents runtime errors and clarifies data intent.

✨ Key Insight: `string?` in modern C# forces you to handle null cases.
   It's the compiler helping you write safer code.
```

**Django/Python Comparison**:
```
🔗 Python vs C# Types:

Python:
  x = 5            # Type inferred at runtime
  name = "John"    # Any type, can change
  active = True    # Boolean (True/False)
  
C#:
  int x = 5;       // Type declared, compile-time checked
  string name = "John"; // Fixed type, can't change
  bool active = true; // Boolean (true/false - lowercase!)
  string? email = null; // Nullable - can be null

Key differences:
  • Python: Dynamic, types changeable, None for null
  • C#: Static, types fixed, null handled explicitly with ?
  • Boolean: Python True/False, C# true/false (lowercase)

💡 Your Python experience: You know variables.
   C# just requires type declaration upfront.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Entities/User.cs (property declarations)
  
Focus on:
  • int Id - integer primary key
  • string UserName - text field
  • bool Active - boolean flag
  • string? someNullableField - nullable reference

🔍 Notice:
  - Type comes BEFORE variable name
  - Properties can be nullable with ?
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: C# Types and Variables
    https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/
```

---

#### 📚 Concept Quiz

```
Q1: Which C# type would you use for a boolean flag?
   A) bool
   B) boolean
   C) int (0 or 1)
   D) Bit

Q2: What is the default value of an `int` variable in C#?
   A) null
   B) 0
   C) undefined
   D) -1

Q3: What does `string?` indicate in modern C#?
   A) Optional string parameter
   B) Nullable reference type
   C) String can be empty
   D) Dynamic string type
```

#### 💻 Coding Task

```
Declare variables for:
- A user's age (integer)
- Their name (string)
- Whether they're active (boolean)
- Their email, which might be null (nullable string)

Example:
int age = 25;
string name = "John Doe";
bool isActive = true;
string? email = null;
```

---

### Task 0.3: Classes & Objects

#### 📚 Teaching Notes

**Complexity**: SIMPLE-MEDIUM (new syntax but familiar concept)

**Concept Summary**:
```
📚 What is it:
C# classes define objects with properties (data) and methods (behavior).
POCO = "Plain Old CLR Object" - simple class without framework dependencies.
Properties use { get; set; } syntax for accessors.

Why it matters:
Classes are the building blocks of C# applications.
Understanding properties vs fields is crucial for EF Core entities.

✨ Key Insight: { get; set; } is how C# does Django fields.
   It's a property with automatic backing storage.
```

**Django/Python Comparison**:
```
🔗 Django Models vs C# Classes:

Django:
  class User(models.Model):
      name = models.CharField(max_length=100)
      email = models.EmailField()
      is_active = models.BooleanField(default=True)
      
      def get_full_name(self):
          return f"{self.name}"

C#:
  public class User
  {
      public string Name { get; set; }      // Property
      public string Email { get; set; }     // Property
      public bool IsActive { get; set; }    // Property
      
      public string GetFullName()           // Method
      {
          return Name;                      // No f-string, just string
      }
  }

Key differences:
  • Django: fields defined as model.XXXField()
  • C#: properties defined as Type Name { get; set; }
  • Django: methods use def
  • C#: methods use return type + method name
  • Django: self for instance reference
  • C#: no self needed, direct property access

💡 Navigation Properties (like Django ForeignKey):
  public Tenant Tenant { get; set; }     // Like Django ForeignKey
  public int TenantId { get; set; }      // Like Django xxx_id field
  public ICollection<User> Users { get; set; }  // Like Django reverse relation
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Entities/User.cs (entire file)
  
Focus on:
  • Line 1-10: Class declaration and inheritance
  • Properties: Id, UserName, Email, Active
  • Navigation properties: Tenant, UserRoles
  • { get; set; } pattern on each property

🔍 Key things to notice:
  - public class User : IdentityUser<int> - inheritance syntax
  - Properties have types, names, and { get; set; }
  - Navigation properties reference other entities
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: C# Classes and Objects
    https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/classes
  
  • Your project: /iam/IAM.Domain/Entities/ (see all entity examples)
```

---

#### 📚 Concept Quiz

```
Q1: What is a POCO class in C#?
   A) A class with special framework attributes
   B) Plain Old CLR Object - simple class without dependencies
   C) A class that inherits from a base
   D) A class with only static methods

Q2: What does `{ get; set; }` mean in a property declaration?
   A) The property is read-only
   B) Auto-implemented property with getter and setter
   C) The property needs manual implementation
   D) The property is private

Q3: In C#, what's the difference between a field and a property?
   A) No difference
   B) Properties have get/set accessors, fields are direct storage
   C) Fields are public, properties are private
   D) Properties are faster
```

#### 📖 Code Reading

```
Read /iam/IAM.Domain/Entities/User.cs and answer:
- What properties does User have?
- Which properties have { get; set; }?
- What does User inherit from?
- What navigation properties exist?
```

#### 🎯 Teach-Back

```
Explain C# classes to someone who knows Django models:
- How properties differ from Django fields
- What navigation properties are (like Django ForeignKey)
- Why { get; set; } syntax exists
```

---

## Level 1: ASP.NET Core Fundamentals

### Task 1.1: Program.cs & Startup

#### 📚 Teaching Notes

**Complexity**: COMPLEX (multi-concept, foundational, novel pattern)
**Action**: PROVIDE MINI-LECTURE

**Concept Summary**:
```
📚 What it is:
Program.cs is ASP.NET Core's entry point. It:
1. Creates a web application builder
2. Registers services in DI container (builder.Services.AddXxx)
3. Configures middleware pipeline (app.UseXxx)
4. Runs the application

Why it matters:
Every request flows through this middleware pipeline.
Order is critical - wrong order breaks auth, error handling, or logging.

✨ Key Insight: Middleware is like a "Russian Doll" - 
   each wraps the next. Request flows IN, response flows OUT.
```

**Django/Python Comparison**:
```
🔗 Django vs ASP.NET Core Startup:

Django:
  settings.py:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        ...
    ]
  
  wsgi.py:
    application = get_wsgi_application()

ASP.NET Core Program.cs:
  builder.Services.AddAuthentication();    // Service registration
  builder.Services.AddDbContext<IAMDbContext>();
  
  app.UseExceptionHandler();               // Middleware pipeline
  app.UseAuthentication();
  app.UseAuthorization();
  
  app.Run();                               // Start server

Similarities:
  • Both define middleware that processes requests
  • Order matters in both
  • Each can intercept/modify request

Differences:
  • Django: Class-based middleware, list in settings
  • ASP.NET: Function-based, inline configuration
  • Django: Linear list concept
  • ASP.NET: Pipeline/Russian Doll nesting concept
  • Django: wsgi.py + settings.py (two files)
  • ASP.NET: Program.cs (one file)

💡 Your Django experience: You understand middleware.
   The concept is the same - just visualized differently.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/Api/Program.cs (89 lines)
  
Focus sections:
  ┌─ Lines 15-45: Service Registration
  │  Look for: AddIAMLogging, AddIAMAuth, AddIAMInfrastructure
  │  Why: These configure dependency injection
  │
  └─ Lines 50-85: Middleware Pipeline
  │  Look for: UseTraceId, UseExceptionHandler, UseAuthentication
  │  Why: This defines request processing order
  │  
  │  Critical order:
  │    TraceId → ExceptionHandler → Authentication → Authorization

🔍 Why this order?
  • TraceId FIRST: Every request gets unique ID for debugging
  • ExceptionHandler EARLY: Catches errors in later middleware
  • Authentication BEFORE Authorization: Must identify user before checking permissions
  • Authorization LAST (before controller): Final permission check
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: ASP.NET Core Middleware
    https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/
  
  • Your project: 
    /iam/CLAUDE.md (startup conventions)
    /iam/README.md (setup instructions)
```

**💡 Mini-Lecture** (COMPLEX topic - provide proactively):
```
💡 Middleware "Russian Doll" Model
───────────────────────────────────

Middleware in ASP.NET Core works like nested Russian dolls.

Request Flow (going IN):
─────────────────────────
  HTTP request arrives
    ↓
  TraceIdMiddleware adds unique ID (e.g., "abc-123")
    ↓
  ExceptionHandler sets up error catcher
    ↓
  RequestLocalization detects language (en or bn-BD)
    ↓
  Authentication validates JWT/Cookie → creates ClaimsPrincipal
    ↓
  Authorization checks permissions for this endpoint
    ↓
  JurisdictionScope sets user's organizational scope
    ↓
  Controller executes → generates response

Response Flow (coming OUT):
─────────────────────────
  Controller returns response
    ↓
  JurisdictionScope passes (no modification)
    ↓
  Authorization passes (already checked)
    ↓
  Authentication passes (already validated)
    ↓
  RequestLocalization passes (language already set)
    ↓
  ExceptionHandler passes (no errors occurred)
    ↓
  TraceIdMiddleware adds ID to response headers
    ↓
  HTTP response sent to client

Visual diagram:
  ┌─────────────────────────────────────────┐
  │ TraceIdMiddleware                        │  ← Outermost
  │ ┌─────────────────────────────────────┐ │
  │ │ ExceptionHandler                     │ │
  │ │ ┌─────────────────────────────────┐ │ │
  │ │ │ Authentication                   │ │ │
  │ │ │ ┌─────────────────────────────┐ │ │ │
  │ │ │ │ Authorization                │ │ │ │
  │ │ │ │ ┌─────────────────────────┐ │ │ │ │
  │ │ │ │ │ Controller               │ │ │ │ │  ← Innermost
  │ │ │ │ │ (Your code runs here)    │ │ │ │ │
  │ │ │ │ └─────────────────────────┘ │ │ │ │
  │ │ │ └─────────────────────────────┘ │ │ │
  │ │ └───────────────────────────────┘ │ │
  │ └─────────────────────────────────────┘ │
  └─────────────────────────────────────────┘

✨ Key insight: Each middleware can:
   1. Do work BEFORE calling next (request path)
   2. Call await next() to pass to inner middleware
   3. Do work AFTER inner middleware completes (response path)

Example - What happens on error:
  Controller throws exception
    ↓
  ExceptionHandler catches it
    ↓
  Generates error response (500 or 400)
    ↓
  TraceIdMiddleware adds trace ID to error response
    ↓
  Client receives error with trace ID for debugging
```

---

#### 📚 Concept Quiz

```
Q1: What does WebApplication.CreateBuilder() do?
   A) Creates a web server
   B) Creates an app builder with configured defaults
   C) Initializes the database
   D) Sets up routing only

Q2: What is the correct middleware order?
   A) UseAuthentication → UseExceptionHandler → UseAuthorization
   B) UseExceptionHandler → UseAuthentication → UseAuthorization
   C) UseAuthorization → UseAuthentication → UseExceptionHandler
   D) Order doesn't matter

Q3: Why does middleware order matter?
   A) Performance optimization
   B) Each middleware can short-circuit the pipeline
   C) Only for logging purposes
   D) It's a framework requirement
```

#### 📖 Code Reading

```
Read /iam/Api/Program.cs and identify:
1. The 5 AddXXX() extension methods and their purpose
2. The middleware pipeline order (all UseXXX calls)
3. Where controllers are mapped
4. The difference between builder.Services and app.Use
```

#### 🔗 Elaboration

```
Q: Compare Program.cs to Django's wsgi.py + settings.py
Q: Why is UseExceptionHandler first in the pipeline?
Q: What would happen if UseAuthentication came before UseExceptionHandler?
Q: How is AddScoped() similar to Django's request context?
```

---

### Task 1.2: Controllers

#### 📚 Teaching Notes

**Complexity**: MEDIUM (new syntax but familiar REST concept)

**Concept Summary**:
```
📚 What it is:
Controllers handle HTTP requests in ASP.NET Core.
Attributes [ApiController], [Route], [HttpGet] define behavior.
ActionResult<T> wraps responses (success data or error status).

Why it matters:
Controllers are where your API logic meets HTTP.
Understanding attributes and ActionResult patterns is essential.

✨ Key Insight: [ApiController] does magic - auto-validation,
   problem detail responses, binding source inference.
```

**Django/Python Comparison**:
```
🔗 Django Views vs ASP.NET Controllers:

Django (DRF):
  class UserViewSet(viewsets.ModelViewSet):
      queryset = User.objects.all()
      serializer_class = UserSerializer
      
      def list(self, request):
          users = self.get_queryset()
          return Response(serializer.data)

ASP.NET Core:
  [ApiController]
  [Route("api/v1/users")]
  public class UserController : ControllerBase
  {
      [HttpGet]
      public async Task<ActionResult<IEnumerable<UserDto>>> GetAll()
      {
          var users = await _userService.GetAllAsync();
          return Ok(users);              // 200 OK with data
      }
      
      [HttpGet("{id}")]
      public async Task<ActionResult<UserDto>> GetById(int id)
      {
          var user = await _userService.GetByIdAsync(id);
          if (user == null) return NotFound();  // 404
          return Ok(user);
      }
  }

Key differences:
  • Django: Class inherits from ViewSet, methods for actions
  • ASP.NET: Attributes mark routes and methods, return ActionResult<T>
  • Django: request parameter for all request data
  • ASP.NET: [FromQuery], [FromBody], [FromRoute] for parameters
  • Django: Response(serializer.data)
  • ASP.NET: Ok(data), NotFound(), BadRequest() etc.

💡 Your Django experience: You know the REST pattern.
   ASP.NET just uses attributes and typed returns instead.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/Api/Controllers/UserController.cs
  /iam/Api/Controllers/TenantController.cs
  
Focus on:
  • [ApiController] attribute - what it provides
  • [Route("api/v1/users")] - URL pattern
  • [HttpGet], [HttpPost], [HttpPut] - method mapping
  • ActionResult<T> return type - success/error wrapper

🔍 Look for:
  - How parameters use [FromQuery], [FromBody]
  - How NotFound(), BadRequest(), Ok() are used
  - Dependency injection of services (_userService)
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: ASP.NET Core Controllers
    https://learn.microsoft.com/en-us/aspnet/core/web-api/
  
  • Your project: /iam/Api/Controllers/ (see all 20+ controllers)
```

---

#### 📚 Concept Quiz

```
Q1: What does [ApiController] attribute provide?
   A) Makes the class a controller
   B) Auto-validation, binding source inference, problem details
   C) Adds authentication
   D) Enables caching

Q2: What does [FromQuery] indicate?
   A) Data comes from query string parameters
   B) Data comes from database query
   C) Data comes from request body
   D) Data comes from route parameter

Q3: What is ActionResult<T>?
   A) A return type that can return T or error status
   B) A base class for controllers
   C) A validation result
   D) A database result wrapper
```

#### 💻 Coding Task

```
Create a simple controller with:
- Route: api/v1/items
- GET endpoint returning all items
- POST endpoint accepting item from body
- GET {id} endpoint returning single item

Use: [ApiController], [Route], [HttpGet], [HttpPost], ActionResult<T>
```

---

### Task 1.3: Dependency Injection

#### 📚 Teaching Notes

**Complexity**: COMPLEX (novel concept for Django, foundational)
**Action**: PROVIDE MINI-LECTURE

**Concept Summary**:
```
📚 What it is:
Dependency Injection (DI) is built into ASP.NET Core.
Services are registered with lifetimes: Transient, Scoped, Singleton.
Constructor injection provides services to controllers/services.

Why it matters:
DI is how ASP.NET Core manages object creation and sharing.
Wrong lifetime = bugs (shared DbContext, stale data, memory leaks).

✨ Key Insight: Scoped = one per HTTP request.
   This is like Django's request.user - available throughout request.
```

**Django/Python Comparison**:
```
🔗 Django vs ASP.NET Core DI:

Django:
  # No built-in DI container
  # Manual service creation or global imports
  
  def my_view(request):
      user = request.user          # Request-scoped
      db = User.objects            # Global database manager
      cache = django.core.cache    # Global cache
      config = settings.DEBUG      # Global config

ASP.NET Core:
  // Built-in DI container
  
  builder.Services.AddScoped<IUserService, UserService>();  // Scoped
  builder.Services.AddSingleton<ICacheService, CacheService>(); // Singleton
  builder.Services.AddTransient<IHelper, Helper>();  // Transient
  
  public class UserController
  {
      private readonly IUserService _userService;  // Injected!
      
      public UserController(IUserService userService)
      {
          _userService = userService;
      }
  }

Lifetime equivalents:
  • Transient = new instance every call (like Python function call)
  • Scoped = one per request (like request.user in Django)
  • Singleton = global (like Django's global imports)

💡 Your Django experience: Django uses globals (settings, ORM).
   ASP.NET uses injected services - cleaner, testable.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/Api/Program.cs (service registration - lines 20-45)
  /iam/Api/Extensions/*Extensions.cs (extension methods)
  /iam/Api/Controllers/UserController.cs (constructor injection)
  
Focus on:
  • builder.Services.AddScoped<TInterface, TImplementation>()
  • Constructor parameters receiving injected services
  
🔍 Look for:
  - How services are registered with different lifetimes
  - How controllers receive services via constructor
  - The pattern: Interface + Implementation registration
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: Dependency Injection in ASP.NET Core
    https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection
```

**💡 Mini-Lecture** (COMPLEX topic):
```
💡 DI Lifetimes Deep Dive
────────────────────────────

Three lifetimes control when services are created:

Transient ─────────────────────────
  Created: Every time it's requested
  
  Example: A helper utility that does simple calculations
  
  code:
    builder.Services.AddTransient<IHelper, Helper>();
  
  Result:
    Request 1: Helper instance A
    Request 1 again: Helper instance B (different!)
    Request 2: Helper instance C
  
  When to use: Lightweight, stateless, no dependencies

Scoped ─────────────────────────────
  Created: Once per HTTP request
  
  Example: DbContext, services that need request context
  
  code:
    builder.Services.AddScoped<IUserService, UserService>();
    builder.Services.AddScoped<IAMDbContext>();
  
  Result:
    Request 1: UserService instance A, DbContext A
    Request 1 (another controller): UserService instance A (same!)
    Request 2: UserService instance B, DbContext B
  
  When to use: Services that need request context, database access
  
  ⚠️ CRITICAL: DbContext MUST be Scoped!
     Singleton DbContext = shared connection = data corruption!

Singleton ──────────────────────────
  Created: Once for application lifetime
  
  Example: Cache, configuration, global state
  
  code:
    builder.Services.AddSingleton<ICacheService, CacheService>();
  
  Result:
    Request 1: CacheService instance A
    Request 2: CacheService instance A (same!)
    Request N: CacheService instance A (same!)
  
  When to use: Caches, configuration, stateless global services
  
  ⚠️ WARNING: Never inject Scoped into Singleton!
     Scoped service would be captured in Singleton's lifetime
     = Captive Dependency bug!

Dependency Flow:
─────────────────────────
  Correct:
    Singleton → can receive Singleton
    Scoped → can receive Singleton, Scoped, Transient
    Transient → can receive Singleton, Scoped, Transient
  
  WRONG (Captive Dependency):
    Singleton → CANNOT receive Scoped!
    The Scoped would be "captive" - never released!
```

---

#### 📚 Concept Quiz

```
Q1: What is Scoped lifetime?
   A) Created once per application
   B) Created every time it's requested
   C) Created once per HTTP request
   D) Created once per user session

Q2: When should you use Singleton?
   A) For database contexts
   B) For lightweight, stateless services or caches
   C) For repositories
   D) Never - it causes issues

Q3: Why shouldn't DbContext be Singleton?
   A) Performance reasons
   B) DbContext is designed for short-lived request scope
   C) It would share connections across users
   D) B and C
```

#### 🔗 Elaboration

```
Q: How is Scoped similar to Django's request context?
Q: Why is Transient the safest default but not always best?
Q: What problems can occur if you inject Scoped into Singleton?
```

#### 🎯 Teach-Back

```
Explain DI lifetimes to a Django developer:
- Transient = "fresh instance each call"
- Scoped = "one instance per request (like request.user)"
- Singleton = "global for app lifetime"
- When to use each and common pitfalls
```

---

## Level 2: Entity Framework Core

### Task 2.1: DbContext

#### 📚 Teaching Notes

**Complexity**: MEDIUM (familiar ORM concept, new syntax)

**Concept Summary**:
```
📚 What it is:
DbContext is EF Core's database context - like Django's ORM manager.
DbSet<T> properties represent tables. OnModelCreating configures mappings.

Why it matters:
DbContext is your gateway to the database.
Understanding its configuration is essential for entity relationships.

✨ Key Insight: OnModelCreating = Django Meta class.
   Fluent API configuration instead of model field options.
```

**Django/Python Comparison**:
```
🔗 Django Models vs EF Core DbContext:

Django:
  class User(models.Model):
      name = models.CharField(max_length=100)
      email = models.EmailField()
      
      class Meta:
          db_table = 'users'
          indexes = ['email']

EF Core:
  public class IAMDbContext : DbContext
  {
      public DbSet<User> Users { get; set; }
      public DbSet<Tenant> Tenants { get; set; }
      
      protected override void OnModelCreating(ModelBuilder modelBuilder)
      {
          modelBuilder.Entity<User>()
              .ToTable("Users", "iam")       // Schema + table
              .HasIndex(u => u.Email);       // Index
      }
  }

Key differences:
  • Django: Model class with Meta inner class
  • EF Core: DbContext with DbSet properties + Fluent API
  • Django: Fields defined in model class
  • EF Core: Entity classes separate, configuration in DbContext
  
💡 Your Django experience: You know models and Meta.
   DbSet = model manager, OnModelCreating = Meta configuration.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Infrastructure/Dal/IAMDbContext.cs
  /iam/IAM.Infrastructure/Dal/Configurations/UserConfiguration.cs
  
Focus on:
  • DbSet<User> Users - table representation
  • HasDefaultSchema("iam") - schema prefix
  • OnModelCreating - configuration assembly
  • Configuration classes - fluent API patterns

🔍 Look for:
  - How entities are registered as DbSet
  - How schema is configured
  - How configuration classes separate entity config
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: Entity Framework Core
    https://learn.microsoft.com/en-us/ef/core/
  
  • Your project: /iam/IAM.Infrastructure/Dal/ (all configurations)
```

---

#### 📚 Concept Quiz

```
Q1: What is DbSet<T>?
   A) A collection type
   B) A table representation for querying entities
   C) A database connection
   D) A migration helper

Q2: What does OnModelCreating do?
   A) Creates the database
   B) Configures entity mappings using Fluent API
   C) Runs migrations
   D) Seeds initial data

Q3: What is HasDefaultSchema("iam")?
   A) Creates a schema named "iam"
   B) Sets the default schema for all tables in this context
   C) Filters queries by schema
   D) Names the database
```

#### 📖 Code Reading

```
Read /iam/IAM.Infrastructure/Dal/IAMDbContext.cs and identify:
1. All DbSet properties (what entities are tracked)
2. The schema configuration
3. What happens in OnModelCreating
```

---

### Task 2.4: LINQ Queries

#### 📚 Teaching Notes

**Complexity**: COMPLEX (deferred execution, nested relationships)
**Action**: PROVIDE MINI-LECTURE

**Concept Summary**:
```
📚 What it is:
LINQ is C# query syntax - SQL-like operations on collections.
Key methods: Where (filter), Select (project), Include (eager load).
Deferred execution: query executes when you enumerate (ToList, First).

Why it matters:
LINQ is how you query EF Core entities.
Understanding deferred execution prevents N+1 query problems.

✨ Key Insight: LINQ query is a recipe, not the result.
   It executes when you "cook" it (ToList, First, Count).
```

**Django/Python Comparison**:
```
🔗 Django ORM vs LINQ:

Django:
  User.objects.filter(active=True)           # Filter
  User.objects.values('name')                # Project
  User.objects.select_related('tenant')      # Eager load
  User.objects.order_by('-created_at')       # Order
  User.objects.first()                       # Get first

LINQ:
  Users.Where(u => u.Active)                 # Filter
  Users.Select(u => u.Name)                  # Project
  Users.Include(u => u.Tenant)               # Eager load
  Users.OrderByDescending(u => u.CreatedAt)  # Order
  Users.FirstOrDefault()                     # Get first

Key equivalents:
  • filter() → Where()
  • values() → Select()
  • select_related() → Include()
  • prefetch_related() → ThenInclude() for collections
  • order_by() → OrderBy() / OrderByDescending()
  • first() → FirstOrDefault()
  • get() → SingleOrDefault() (throws if not exactly one)

💡 Your Django experience: You know Django ORM.
   LINQ methods are the same concepts, different syntax.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Infrastructure/Repositories/UserRepository.cs
  /iam/IAM.Application/Services/UserService.cs
  
Focus on:
  • .Where() clauses - filtering
  • .Include() and .ThenInclude() - relationship loading
  • .FirstOrDefault() - getting single result
  • .ToListAsync() - executing the query

🔍 Look for:
  - How Include loads Tenant (like select_related)
  - How ThenInclude loads nested relationships
  - When query executes (ToList, First, Count)
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: LINQ in C#
    https://learn.microsoft.com/en-us/dotnet/csharp/linq/
  
  • EF Core Querying:
    https://learn.microsoft.com/en-us/ef/core/querying/
```

**💡 Mini-Lecture** (COMPLEX topic):
```
💡 LINQ Deferred Execution & Include/ThenInclude
─────────────────────────────────────────────────

Deferred Execution:
───────────────────────
LINQ query is NOT executed when you write it.
It's executed when you "materialize" it.

Example:
  var query = Users.Where(u => u.Active);   // NOT executed yet!
  
  // Later...
  var result = query.ToList();              // NOW it executes!
  var first = query.FirstOrDefault();       // NOW it executes!
  var count = query.Count();                // NOW it executes!

Why this matters:
  • You can compose queries step by step
  • Adding .Include() doesn't run query
  • Only materialization (ToList, First, etc.) runs SQL

✨ Key Insight: Think of LINQ as a recipe card.
   Writing the recipe doesn't cook the meal.
   Calling ToList cooks it!

Include() vs ThenInclude():
─────────────────────────────

Include() loads directly related entity:
  Users.Include(u => u.Tenant)
  
  SQL generated:
    SELECT users.*, tenants.*
    FROM users LEFT JOIN tenants ON users.tenant_id = tenants.id
  
ThenInclude() loads nested relationships:
  Users.Include(u => u.Tenant)
        .ThenInclude(t => t.BusinessEntity)
  
  SQL generated:
    SELECT users.*, tenants.*, business_entities.*
    FROM users 
    LEFT JOIN tenants ON users.tenant_id = tenants.id
    LEFT JOIN business_entities ON tenants.be_id = business_entities.id

Deep nesting example:
  Users.Include(u => u.UserRoles)           // Load roles
        .ThenInclude(ur => ur.Role)          // Load role details
        .ThenInclude(r => r.RolePermissions) // Load permissions
        .ThenInclude(rp => rp.Permission)    // Load permission details
  
  This loads: User → UserRoles → Role → RolePermissions → Permission
  Equivalent Django: Multiple prefetch_related calls

N+1 Problem Prevention:
─────────────────────────────
WITHOUT Include:
  var users = Users.ToList();
  foreach (var user in users)
  {
      var tenant = user.Tenant;  // SEPARATE query for each!
  }
  // Result: 1 query for users + N queries for tenants = N+1 queries!

WITH Include:
  var users = Users.Include(u => u.Tenant).ToList();
  foreach (var user in users)
  {
      var tenant = user.Tenant;  // Already loaded! No extra query
  }
  // Result: 1 query only, tenant included in same query

💡 Always use Include() for relationships you'll access!
   Django equivalent: Always use select_related/prefetch_related.
```

---

#### 📚 Concept Quiz

```
Q1: What does .Include() do?
   A) Adds a condition to the query
   B) Eager loads related entities
   C) Includes the entity in results
   D) Includes debugging info

Q2: What is the difference between FirstOrDefault() and SingleOrDefault()?
   A) No difference
   B) FirstOrDefault returns first match, SingleOrDefault expects exactly one
   C) SingleOrDefault is faster
   D) FirstOrDefault throws if multiple found

Q3: What does .Where(u => u.Active) translate to?
   A) SELECT * FROM Users
   B) SELECT * FROM Users WHERE Active = 1
   C) UPDATE Users SET Active = 1
   D) DELETE FROM Users WHERE Active = 0
```

#### 💻 Coding Task

```
Write LINQ queries for:

1. Get all active users with their tenants:
   _context.Users
     .Where(u => u.Status == UserStatus.Active)
     .Include(u => u.Tenant)
     .ToList();

2. Get first 10 users ordered by creation date:
   _context.Users
     .OrderByDescending(u => u.CreatedAt)
     .Take(10)
     .ToList();

3. Count users in a specific tenant:
   _context.Users
     .Where(u => u.TenantId == tenantId)
     .Count();

4. Get user with roles and permissions:
   _context.Users
     .Include(u => u.UserRoles)
       .ThenInclude(ur => ur.Role)
         .ThenInclude(r => r.RolePermissions)
           .ThenInclude(rp => rp.Permission)
     .FirstOrDefault(u => u.Id == userId);
```

#### 🔗 Elaboration

```
Q: Compare LINQ .Include() to Django's .select_related()
Q: Compare LINQ .Where() to Django's .filter()
Q: Why use ThenInclude() for nested relationships?
Q: How does EF Core translate LINQ to SQL?
```

---

## Level 3: Clean Architecture

### Task 3.1: Layer Responsibilities

#### 📚 Teaching Notes

**Complexity**: COMPLEX (architectural concept, foundational)
**Action**: PROVIDE MINI-LECTURE

**Concept Summary**:
```
📚 What it is:
Clean Architecture separates code into layers:
- Domain: Entities, enums (ZERO dependencies)
- Application: Services, DTOs, validators (depends on Domain)
- Infrastructure: Database, external services (depends on Domain + Application)
- API: Controllers, middleware (depends on everything)

Why it matters:
Layer separation enables testing, maintainability, and flexibility.
Domain's zero dependencies keep business logic pure.

✨ Key Insight: Domain layer = your business rules.
   Everything else supports Domain, Domain doesn't know about them.
```

**Django/Python Comparison**:
```
🔗 Django vs Clean Architecture:

Django (Implicit layers):
  models.py          → "Domain-ish" (entities + database)
  views.py           → "Application-ish" (business logic)
  settings.py        → "Infrastructure-ish" (config)
  urls.py            → "API-ish" (routing)
  
  Problem: Models depend on Django ORM (not pure Domain)

Clean Architecture:
  IAM.Domain/        → Pure entities (no framework dependencies!)
  IAM.Application/   → Services, DTOs, validators
  IAM.Infrastructure/ → DbContext, repositories
  Api/               → Controllers, middleware
  
  Benefit: Domain is pure - can test without database!

Key differences:
  • Django: Layers implicit, models tied to framework
  • Clean Architecture: Layers explicit, Domain pure
  
💡 Your Django experience: You know Django's structure.
   Clean Architecture makes it explicit and purer.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Entities/ (pure entities)
  /iam/IAM.Application/Services/ (business logic)
  /iam/IAM.Infrastructure/Repositories/ (database)
  /iam/Api/Controllers/ (API endpoints)
  
Focus on:
  • Domain: Entities have no imports from Infrastructure/Application
  • Application: Services import Domain entities
  • Infrastructure: Imports Domain + Application interfaces
  • API: Imports everything, orchestrates

🔍 Dependency verification:
  - Check Domain imports → should only be System, no project references
  - Check Application imports → should include Domain, not Infrastructure
  - Check Infrastructure imports → includes Domain + Application
```

**Documentation**:
```
📚 Learn more:
  • Clean Architecture by Steve Smith (article/book)
  
  • Your project: 
    /iam/CLAUDE.md (architecture section)
    /iam/README.md (project structure)
```

**💡 Mini-Lecture** (COMPLEX topic):
```
💡 Clean Architecture Layer Deep Dive
───────────────────────────────────────

The Dependency Rule:
───────────────────────
Dependencies flow INWARD only:
  
  API → Infrastructure → Application → Domain
        ↓              ↓            ↓
        (can depend)   (can depend) (NO dependencies!)

Never:
  Domain → Application (WRONG!)
  Domain → Infrastructure (WRONG!)
  Application → Infrastructure (WRONG!)

Why this rule?
  • Domain stays pure - business rules untouched by framework
  • Application defines what it needs (interfaces)
  • Infrastructure provides implementations
  • API orchestrates everything

Layer Contents:
───────────────────────

Domain (IAM.Domain/):
  • Entities: User, Tenant, Organization
  • Enums: IAMPermission, UserStatus
  • Exceptions: IAMException
  • Types: IAMJurisdictionObject
  • ZERO dependencies - pure C# classes

Application (IAM.Application/):
  • Services: UserService, TenantService (business logic)
  • DTOs: UserDto, CreateUserDto (API shapes)
  • Validators: CreateUserValidator (FluentValidation)
  • Repository Interfaces: IUserRepository (contracts)
  • Depends on: Domain only

Infrastructure (IAM.Infrastructure/):
  • DbContext: IAMDbContext
  • Repositories: UserRepository (implements IUserRepository)
  • External services: EmailService, FileStorage
  • Depends on: Domain + Application (implements interfaces)

API (Api/):
  • Controllers: UserController, TenantController
  • Middleware: ExceptionHandler, TraceIdMiddleware
  • Program.cs: Startup configuration
  • Depends on: Everything (orchestrates all)

Testing Benefit:
───────────────────────
Because Domain has no dependencies:
  • Test business rules without database
  • Mock Infrastructure in Application tests
  • Fast unit tests, slow integration tests only for Infrastructure

✨ Key Insight: Repository interfaces in Application layer
   let you swap Infrastructure implementations!
   (Mock for tests, real for production)
```

---

#### 📚 Concept Quiz

```
Q1: Which layer has NO dependencies?
   A) Infrastructure
   B) Application
   C) Domain
   D) API

Q2: What goes in the Application layer?
   A) Database context
   B) Entities
   C) Services, DTOs, Validators, Repository interfaces
   D) Controllers

Q3: Why does Domain have zero dependencies?
   A) Performance
   B) To keep business logic pure and portable
   C) Convention
   D) Framework requirement
```

#### 🔗 Elaboration

```
Q: Compare Clean Architecture layers to Django's structure
Q: Why is Domain the "core" with no dependencies?
Q: What would break if Domain referenced Infrastructure?
Q: How do repository interfaces in Application enable testing?
```

#### 🎯 Teach-Back

```
Explain Clean Architecture to a Django developer:
- Domain = pure business entities (no Django models dependency)
- Application = services/logic (Django views/business logic)
- Infrastructure = database/external (Django ORM, settings)
- API = controllers (Django urls + view dispatch)
- Dependency flow: Domain → Application → Infrastructure → API
```

---

## Level 4: Authentication & Authorization

### Task 4.1: ASP.NET Identity

#### 📚 Teaching Notes

**Complexity**: MEDIUM (familiar auth concept)

**Concept Summary**:
```
📚 What it is:
ASP.NET Identity handles user management, passwords, roles.
IdentityUser is base user class (like Django AbstractUser).
Claims are key-value pairs in user's identity token.

Why it matters:
Identity integrates with OpenIddict for OAuth/OIDC.
Understanding Identity entities is needed for IAM customization.

✨ Key Insight: Claims are like Django user attributes,
   but stored in JWT token, not database.
```

**Django/Python Comparison**:
```
🔗 Django Auth vs ASP.NET Identity:

Django:
  class User(AbstractUser):
      email = models.EmailField()
      is_staff = models.BooleanField()
  
  user = User.objects.create_user(...)
  user = authenticate(request, username=..., password=...)
  login(request, user)

ASP.NET Identity:
  public class User : IdentityUser<int>
  {
      public string Email { get; set; }
  }
  
  await _userManager.CreateAsync(user, password);
  var result = await _signInManager.PasswordSignInAsync(...);

Key equivalents:
  • AbstractUser → IdentityUser<T>
  • User.objects → UserManager
  • authenticate → SignInManager.PasswordSignInAsync
  • login → SignInManager (sets cookie)
  • user.email → Claims in token (sub, name, email, role)

💡 Your Django experience: You know user models and auth.
   Identity extends a base class, similar pattern.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Entities/User.cs (IdentityUser inheritance)
  /iam/IAM.Infrastructure/Authorization/IAMClaimsPrincipalFactory.cs
  /iam/Api/Controllers/AccountController.cs (login/registration)
  
Focus on:
  • IdentityUser<int> inheritance
  • UserManager, SignInManager usage
  • Claims generation in IAMClaimsPrincipalFactory

🔍 Look for:
  - User extends IdentityUser<int> (int as PK type)
  - Claims added: sub, name, email, role, iam_user_id, iam_role_grants
```

**Documentation**:
```
📚 Learn more:
  • Microsoft Learn: ASP.NET Core Identity
    https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity
```

---

#### 📚 Concept Quiz

```
Q1: What is IdentityUser<int>?
   A) A user class with int as primary key type
   B) A user with integer age
   C) A numeric user identifier
   D) A user with int permissions

Q2: What does UserManager provide?
   A) User CRUD operations and password management
   B) Database management
   C) Role management
   D) Token generation

Q3: What is a Claim?
   A) A database assertion
   B) A key-value pair in user's identity token
   C) A permission check
   D) A login credential
```

---

### Task 4.5: JBAC (Jurisdiction-Based Access Control)

#### 📚 Teaching Notes

**Complexity**: COMPLEX (unique IAM pattern)

**Concept Summary**:
```
📚 What it is:
JBAC = Jurisdiction-Based Access Control.
Permissions scoped by organizational hierarchy: BE → Tenant → App → Org.
IAMJurisdictionObject defines scope for permission checks.

Why it matters:
JBAC is IAM's custom permission system.
Understanding it is essential for scoped operations.

✨ Key Insight: Same permission can be granted at different scopes.
   "Manage Users" at Tenant scope = manage tenant's users.
   "Manage Users" at Org scope = manage org's users only.
```

**Django/Python Comparison**:
```
🔗 Django Permissions vs JBAC:

Django:
  user.has_perm('users.add_user')           # Global permission
  user.has_perm('users.change_user', obj)   # Object-level (rare)
  
  Groups for role-like behavior, but flat structure.

JBAC:
  CheckUserPermission(IAMPermission.ManageUsers, jurisdiction);
  
  jurisdiction = new IAMJurisdictionObject
  {
      BusinessEntityId = 1,    // Scope to BE
      TenantId = 10,           // Scope to Tenant
      OrganizationId = 100     // Scope to Org
  };
  
  Hierarchy: Super Admin → BE Admin → Tenant Admin → App Admin → Org Admin

Key differences:
  • Django: Flat permissions, optional object-level
  • JBAC: Hierarchical, every permission scoped by jurisdiction
  • Django: Groups for roles
  • JBAC: IAMRole with permission grants + jurisdiction scope
  
💡 Your Django experience: Django has simple permissions.
   JBAC adds scope hierarchy - powerful but complex.
```

**Code Pointer**:
```
📖 Reference Files:
  /iam/IAM.Domain/Enums/IAMPermission.cs (44 permissions)
  /iam/IAM.Domain/Types/IAMJurisdictionObject.cs
  /iam/IAM.Application/Services/AccessControlService.cs
  /iam/IAM.Domain/Entities/IAMRole.cs
  
Focus on:
  • IAMPermission enum - granular permissions
  • IAMJurisdictionObject - scope container
  • CheckUserPermission() - authorization method
  • IAMUserLevel enum - hierarchy levels

🔍 Look for:
  - How jurisdiction object contains scope IDs
  - How CheckUserPermission throws on denial
  - How UserHasPermission returns bool (no throw)
```

**Documentation**:
```
📚 Learn more:
  • Your project: 
    /iam/CLAUDE.md (JBAC section)
    /iam/IAM.Application/Services/AccessControlService.cs
```

---

#### 📚 Concept Quiz

```
Q1: What is JBAC?
   A) Just Basic Access Control
   B) Jurisdiction-Based Access Control - permissions scoped by hierarchy
   C) Java-Based Access Control
   D) JSON-Based Access Control

Q2: What does IAMJurisdictionObject contain?
   A) User preferences
   B) Scope IDs (BE, Tenant, App, Org) for permission checking
   C) Audit logs
   D) Session data

Q3: What happens when CheckUserPermission() fails?
   A) Returns false
   B) Throws IAMException with permission denied
   C) Logs warning
   D) Redirects to login
```

#### 🔗 Elaboration

```
Q: Compare JBAC to Django's permission system
Q: Why scope permissions by jurisdiction hierarchy?
Q: How does Super Admin differ from Tenant Admin in JBAC?
```

---

## Frontend Track

### Task 0.1: useState Hook

#### 📚 Teaching Notes

**Complexity**: SIMPLE (new syntax but straightforward)

**Concept Summary**:
```
📚 What it is:
useState is React's state hook for functional components.
Returns [value, setter] tuple. Updates trigger re-render.

Why it matters:
Hooks replaced class component state - fundamental React pattern.

✨ Key Insight: Functional update (prev => prev + 1) 
   avoids stale closure bugs in async updates.
```

**Old React Comparison**:
```
🔗 React 6 years ago vs Modern React:

Old React (class components):
  class Counter extends React.Component {
      state = { count: 0 };
      
      increment = () => {
          this.setState({ count: this.state.count + 1 });
      }
  }

Modern React (hooks):
  function Counter() {
      const [count, setCount] = useState(0);
      
      const increment = () => {
          setCount(prev => prev + 1);  // Functional update
      }
  }

Key differences:
  • this.state → useState array
  • this.setState → setter function
  • Functional update avoids stale closures

💡 Your React experience (6 years ago): You know class state.
   useState is simpler - just array destructuring!
```

**Code Pointer**:
```
📖 Reference Files:
  /iam-frontend/components/users/UserCreateFormModal.tsx
  /iam-frontend/lib/hooks/useCurrentUser.ts
  
Focus on:
  • useState declarations at top of component
  • Functional updates: setX(prev => ...)
  • Object state: setState(prev => ({ ...prev, field: value }))
```

---

#### 📚 Concept Quiz

```
Q1: What does useState return?
   A) Just the value
   B) A tuple [value, setterFunction]
   C) An object { value, set }
   D) A promise

Q2: Why use setValue(prev => prev + 1) instead of setValue(value + 1)?
   A) No difference
   B) Ensures you're working with latest state, not stale closure
   C) It's faster
   D) Required syntax

Q3: How do you update an object in state?
   A) state.field = newValue
   B) setState({ field: newValue })
   C) setState({ ...state, field: newValue })
   D) setState(state.field = newValue)
```

#### 💻 Coding Task

```
Create a counter component:
- Initial count: 0
- Button to increment
- Button to decrement
- Display current count

Use useState with functional update for increment.
```

---

### Task 0.2: useEffect Hook

#### 📚 Teaching Notes

**Complexity**: MEDIUM (side effects, cleanup pattern)

**Concept Summary**:
```
📚 What it is:
useEffect runs side effects after render.
Dependency array controls when it runs.
Cleanup function runs before next effect or unmount.

Why it matters:
Understanding useEffect prevents memory leaks and stale data.

✨ Key Insight: [] = run once on mount.
   No deps = run every render (avoid!).
```

**Old React Comparison**:
```
🔗 React lifecycle vs useEffect:

Old React:
  componentDidMount() {       // Run once on mount
      fetchData();
  }
  
  componentDidUpdate() {      // Run on update
      if (prevProps.id !== this.props.id) {
          fetchData();
      }
  }
  
  componentWillUnmount() {    // Cleanup
      cancelRequest();
  }

Modern React:
  useEffect(() => {
      fetchData();
      
      return () => cancelRequest();  // Cleanup
  }, [id]);  // Dependency - runs when id changes
  
  // [] = mount only (componentDidMount + componentWillUnmount)
  // [id] = mount + id changes
  // no deps = every render (usually bad!)

💡 Your React experience: You know lifecycle methods.
   useEffect combines them all into one hook!
```

**Code Pointer**:
```
📖 Reference Files:
  /iam-frontend/lib/hooks/useCurrentUser.ts
  /iam-frontend/components/users/UserManagementPage.tsx
  
Focus on:
  • useEffect with [] - mount-only
  • useEffect with [dep] - dependency tracking
  • Return cleanup function
```

---

#### 📚 Concept Quiz

```
Q1: When does useEffect with [] dependency run?
   A) Every render
   B) Only on mount
   C) Only on unmount
   D) Never

Q2: What does the cleanup function do?
   A) Clears the effect result
   B) Runs before next effect or on unmount
   C) Resets state
   D) Handles errors

Q3: Why split effects into multiple useEffect calls?
   A) Performance
   B) Separate concerns, each with own dependencies
   C) Required by React
   D) Easier debugging
```

---

## Task Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Ready | Teaching notes + Quiz complete |
| 🚧 Draft | Partially written |
| ⏳ Pending | Not yet written |

---

## Adding New Task Content

To add content for a new task:

```markdown
### Task X.Y: [Topic Name]

#### 📚 Teaching Notes

**Complexity**: SIMPLE / MEDIUM / COMPLEX
**Action**: SUMMARY-ONLY / PROVIDE MINI-LECTURE

**Concept Summary**:
[2-3 sentence summary]

**Django/Python Comparison**:
[Side-by-side code comparison]

**Code Pointer**:
[Reference file + lines + focus areas]

**Documentation**:
[Links to docs]

**💡 Mini-Lecture** (if COMPLEX):
[Detailed walkthrough]

---

#### 📚 Concept Quiz
[multiple choice questions]

#### 📖 Code Reading
[reference file questions]

#### 💻 Coding Task
[code writing challenge]

#### 🔗 Elaboration
[connection/why questions]

#### 🎯 Teach-Back
[explain-in-own-words prompt]
```