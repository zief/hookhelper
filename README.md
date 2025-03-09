# hookhelper
Objection Plugin that can help you during the dynamic analysis process.
This plugin is developed to learn how far I can use Objection to help activities during dynamic analysis. 

# Usage

1. Clone this repo
```
git clone
```

2. Load the plugin to Objection

```
plugin load /<path-to-the-plugin>/hookhelper
```

### changeVar
```
 plugin hookhelper changeVar --package-name <package_name> --class-name <class_name> --variable-name <variable_name> --new-value <new_value> <--int|--string|--boolean>

            Options:
            --package-name  Specify the full package name of the Java class.
            --class-name    Specify the Java class name whose static variable is to be changed.
            --variable-name Specify the static variable name to change.
            --new-value     Specify the new value for the static variable.
            --int           Specify if the new value is of type integer.
            --string        Specify if the new value is of type string.
            --boolean       Specify if the new value is of type boolean.
            -h, --help      Show this help message and exit.

            Description:
            Dynamically change the value of a static variable of a Java class. The new value can be of
            type integer, string, or boolean.

            Examples:
            - Change an integer static variable:
            plugin hookhelper changeVar --package-name com.example.myapp --class-name MyClass --variable-name MY_VAR --new-value 123 --int

            - Change a string static variable:
            plugin hookhelper changeVar --package-name com.example.myapp --class-name MyClass --variable-name MY_VAR --new-value "hello" --string

            - Change a boolean static variable:
            plugin hookhelper changeVar --package-name com.example.myapp --class-name MyClass --variable-name MY_VAR --new-value true --boolean
```

### hookConstructor
```
plugin hookhelper hookConstructor --class-name <class_name> [--args-int <integer>] [--args-string <string>] [--args-boolean <true/false>]...

            Options:
            --class-name   Specify the full name of the Java class you want to hook.
            --args-int     Provide an integer argument to pass to the constructor.
            --args-string  Provide a string argument to pass to the constructor.
            --args-boolean Provide a boolean argument (true/false) to pass to the constructor.
            -h, --help     Show this help message and exit.

            Description:
            Dynamically hook the constructor of a specified Java class with flexible argument types.
            You can provide multiple arguments in sequence using --args-int, --args-string, and --args-boolean.

            Examples:
            - Hook a constructor with integers and a string:
                plugin hookhelper hookConstructor --class-name com.example.MyClass --args-int 123 --args-int 456 --args-string "test"

            - Hook a constructor with a mix of argument types:
               plugin hookhelper hookConstructor --class-name com.example.MyClass --args-int 789 --args-boolean true --args-string "hello"
```

### invokeMethod
```
plugin hookhelper invokeMethod --package-name <package_name> --class-name <class_name> --method <method_name> [--args-int <integer>] [--args-string <string>] [--args-boolean <true/false>]... [--return-value]

            Options:
            --package-name  Specify the full package name of the Java class.
            --class-name    Specify the Java class name whose method is to be invoked.
            --method        Specify the method name to invoke.
            --args-int      Specify an integer argument for the method (can be repeated).
            --args-string   Specify a string argument for the method (can be repeated).
            --args-boolean  Specify a boolean argument (true/false) for the method (can be repeated).
            --return-value  Return and display the result of the invoked method.
            -h, --help      Show this help message and exit.

            Description:
            Dynamically invoke a method on a Java class instance with flexible arguments, including
            support for integer, string, and boolean parameters.

            Examples:
            - Invoke a method with integers and strings:
               plugin hookhelper invokeMethod --package-name com.example.myapp --class-name MyClass --method myMethod --args-int 123 --args-string "hello" --args-boolean true

            - Invoke a method and display its return value:
                plugin hookhelper invokeMethod --package-name com.example.myapp --class-name MyClass --method getResult --return-value
```

### invokeNonStatic
```
plugin hookhelper invokeNonStatic --package-name <package_name> --class-name <class_name> --method <method>
                        [--args-int <integer>] [--args-string <string>] [--args-boolean <true/false>]... [--return-value]

            Options:
            --package-name  Specify the full package name of the Java class.
            --class-name    Specify the Java class name whose method is to be invoked.
            --method        Specify the method name to invoke.
            --args-int      Specify an integer argument for the method (can be repeated).
            --args-string   Specify a string argument for the method (can be repeated).
            --args-boolean  Specify a boolean argument (true/false) for the method (can be repeated).
            --return-value  Return and display the result of the invoked method.
            -h, --help      Show this help message and exit.

            Description:
            Dynamically invoke a method on a Java class instance with flexible arguments, including
            support for integer, string, and boolean parameters.

            Examples:
            - Invoke a method with integers and strings:
            plugin hookhelper invokeNonStatic --package-name com.example.myapp --class-name MyClass --method myMethod --args-int 123 --args-string "hello" --args-boolean true

            - Invoke a method and display its return value:
            plugin hookhelper invokeNonStatic --package-name com.example.myapp --class-name MyClass --method getResult --return-value
```

### invoke_method_with_object
```
plugin hookhelper invoke_method_with_object --class-name <class_name> --method-name <method_name> --object-class <object_class>
                        --object-property-<type> <property_name>(<value>)... [--debug]

            Options:
            --class-name         Specify the full name of the Java class.
            --method-name        Specify the method name to invoke.
            --object-class       Specify the full name of the object class to be created.
            --object-property    Specify the properties of the object with type, name, and value. Use multiple times for different properties.
                                Format: --object-property-<type> <property_name>(<value>)
                                Example: --object-property-int age(30) --object-property-string name("John")
            --debug              Enable debug mode for additional logging.
            -h, --help           Show this help message and exit.

            Description:
            Dynamically invoke a method on a Java class instance with a flexible object instance. The object properties can be specified with different types.

            Examples:
            - Invoke a method with an object having integer and string properties:
            plugin hookhelper invoke_method_with_object --class-name com.example.MyClass --method-name myMethod --object-class com.example.MyObject
                --object-property-int age(30) --object-property-string name("John")

            - Invoke a method in debug mode:
            plugin hookhelper invoke_method_with_object --class-name com.example.MyClass --method-name myMethod --object-class com.example.MyObject
                --object-property-int age(30) --object-property-string name("John") --debug
```
