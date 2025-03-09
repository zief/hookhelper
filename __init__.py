__description__ = "A plugin to help hook and invoke specific Java methods on class instances and change static variables"

import sys
import re
from objection.utils.plugin import Plugin

s = """
rpc.exports = {
    invokeMethod: function(packageName, className, methodName, params = [], paramTypes = [], returnValue = false) {
        Java.perform(function() {
            try {
                console.log("Starting method invocation for: " + packageName + '.' + className + '.' + methodName);
                var clazz = Java.use(packageName + '.' + className);
                console.log("Class loaded successfully.");

                // Use Java.choose to locate an instance of the class
                Java.choose(packageName + '.' + className, {
                    onMatch: function(instance) {
                        console.log("Instance found");

                        try {
                            // Resolve the method with the correct overload based on parameter types
                            var methodToInvoke = instance[methodName].overload.apply(instance[methodName], paramTypes);
                            console.log("Method overload resolved.");

                            // Invoke the method with provided parameters
                            var result;
                            if (params.length > 0) {
                                result = methodToInvoke.apply(instance, params);
                            } else {
                                result = methodToInvoke.call(instance);
                            }
                            console.log("Method invoked successfully.");

                            // Return the result if specified
                            if (returnValue) {
                                console.log("Method result: " + result);
                                send('Method result: ' + result);
                            }

                            send('Method invoked successfully: ' + packageName + '.' + className + '.' + methodName);
                        } catch (innerErr) {
                            console.log("Error during method invocation: " + innerErr.message);
                            send('Error during method invocation: ' + innerErr.message);
                        }
                    },
                    onComplete: function() {
                        console.log('Instance search complete.');
                    }
                });
            } catch (e) {
                console.log('Error invoking method: ' + e.message);
                send('Error invoking method: ' + e.message);
            }
        });
    },
    changeStaticVariable: function(packageName, className, variableName, newValue, valueType) {
        Java.perform(function() {
            try {
                console.log("Starting static variable change for: " + packageName + '.' + className + '.' + variableName);
                var clazz = Java.use(packageName + '.' + className);
                console.log("Class loaded successfully.");

                // Convert the new value to the specified type
                if (valueType === 'int') {
                    clazz[variableName].value = parseInt(newValue);
                } else if (valueType === 'boolean') {
                    clazz[variableName].value = (newValue.toLowerCase() === 'true');
                } else {
                    clazz[variableName].value = newValue;  // Assume string if not int or boolean
                }

                console.log("Static variable changed successfully.");
                send('Static variable ' + variableName + ' changed to: ' + newValue);
            } catch (e) {
                console.log('Error changing static variable: ' + e.message);
                send('Error changing static variable: ' + e.message);
            }
        });
    },
    invokeNonStaticMethod: function(packageName, className, method, params = [], paramTypes = [], returnValue = false) {
        Java.perform(function() {
            try {
                console.log("Starting non-static method invocation for: " + packageName + '.' + className + '.' + method);
                var clazz = Java.use(packageName + '.' + className);
                var instance = clazz.$new();  // Create a new instance of the class
                console.log("Instance created successfully.");

                // Resolve the method with the correct overload based on parameter types
                var methodToInvoke = instance[method].overload.apply(instance[method], paramTypes);
                console.log("Method overload resolved.");

                var result;
                if (params.length > 0) {
                    result = methodToInvoke.apply(instance, params);
                } else {
                    result = methodToInvoke.call(instance);
                }
                console.log("Method invoked successfully.");

                // Return the result if specified
                //console.log("Return value is : returnValue")
                if (returnValue) {
                    console.log("Method result: " + result);
                    send('Method result: ' + result);
                }

                send('Method invoked successfully: ' + packageName + '.' + className + '.' + method);
            } catch (e) {
                console.log('Error invoking non-static method: ' + e.message);
                send('Error invoking non-static method: ' + e.message);
            }
        });
    },
    invokeMethodWithObject: function(className, methodName, objectClass, objectProperties, debug) {
        Java.performNow(function() {
            var clazz = Java.use(className);
            if (debug) {
                console.log("Class loaded: " + className);
            }

            Java.choose(className, {
                onMatch: function(instance) {
                    if (debug) {
                        console.log("Instance found: " + className);
                    }

                    var obj = Java.use(objectClass).$new();
                    if (debug) {
                        console.log("Object created: " + objectClass);
                    }

                    objectProperties.forEach(function(prop) {
                        var propName = prop.name;
                        var propValue = prop.value;
                        if (debug) {
                            console.log("Setting " + propName + " to " + propValue);
                        }
                        if (prop.type === 'int') {
                            obj[propName].value = parseInt(propValue, 10);
                        } else if (prop.type === 'string') {
                            obj[propName].value = propValue;
                        } else if (prop.type === 'boolean') {
                            obj[propName].value = propValue === 'true';
                        }
                    });

                    if (debug) {
                        console.log("Invoking method " + methodName);
                    }
                    instance[methodName](obj);
                    if (debug) {
                        console.log("Method invoked successfully: " + className + "." + methodName);
                    }
                    send('Method invoked successfully: ' + className + '.' + methodName);
                },
                onComplete: function() {
                    if (debug) {
                        console.log("Completed choosing instance of " + className);
                    }
                }
            });
        });
    },
    hookConstructor: function(className, args) {
        Java.perform(function() {
            var TargetClass = Java.use(className); // Use the class name dynamically
            
            var overloadMatch = TargetClass.$init.overloads.find(function(overload) {
                return overload.argumentTypes.length === args.length;
            });

            if (!overloadMatch) {
                console.log("No matching overload for the given arguments.");
                return;
            }

            overloadMatch.implementation = function() {
                console.log('Original constructor called with: ' + JSON.stringify(arguments));
                send('Hooking constructor with arguments: ' + JSON.stringify(args));

                for (var i = 0; i < args.length; i++) {
                    arguments[i] = args[i]; // Overwrite arguments with the provided values
                }

                return this.$init.apply(this, arguments); // Call the constructor with the modified arguments
            };
        });
    }
}

"""

class HookHelper(Plugin):
    """ HookHelper is a plugin to invoke specific Java methods on class instances and change static variables """

    def __init__(self, ns):
        """
            Creates a new instance of the plugin

            :param ns:
        """

        # plugin sources are specified, so when the plugin is loaded it will not
        # try and discover an index.js next to this file.
        self.script_src = s
        self.debug = False

        # as script_src is specified, a path is not necessary. this is simply an
        # example of an alternate method to load a Frida script
        # self.script_path = os.path.join(os.path.dirname(__file__), "script.js")

        implementation = {
            'meta': 'Invoke specific Java methods on class instances and change static variables',
            'commands': {
                'invokeMethod': {
                    'meta': 'Invoke a specific Java class method on an instance',
                    'exec': self.invoke_method
                },
                'changeVar': {
                    'meta': 'Change a static variable of a Java class',
                    'exec': self.change_static_variable
                },
                'invokeNonStatic': {
                    'meta': 'Invoke a specific Java class method of a non-static class',
                    'exec': self.invoke_non_static_method
                },
                'invoke_method_with_object': {
                    'meta': 'Invoke a method with an object',
                    'exec': self.invoke_method_with_object
                },
                'hookConstructor': {
                    'meta': 'Hook the constructor of a Java class',
                    'exec': self.hook_constructor
                }
            
            }
        }

        super().__init__(__file__, ns, implementation)

        self.inject()

    def invoke_method(self, args: list):
        """
            Invokes a specific Java class method on an instance and optionally returns the result.

            :param args: Command-line style arguments for invoking a method
            :return:
        """

        # Help message for the invoke_method command
        help_text = """
            Usage:
            plugin hookhelper invokeMethod --package-name <package_name> --class-name <class_name> --method <method_name> 
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
               plugin hookhelper invokeMethod --package-name com.example.myapp --class-name MyClass --method myMethod --args-int 123 --args-string "hello" --args-boolean true

            - Invoke a method and display its return value:
                plugin hookhelper invokeMethod --package-name com.example.myapp --class-name MyClass --method getResult --return-value
            """

        # Display the help message if requested
        if "-h" in args or "--help" in args:
            print(help_text)
            return

        # Ensure required arguments are present
        if not any(arg.startswith("--package-name") for arg in args) or \
        not any(arg.startswith("--class-name") for arg in args) or \
        not any(arg.startswith("--method") for arg in args):
            print("Error: Missing required arguments (--package-name, --class-name, or --method). Use -h or --help for usage information.")
            return

        # Initialize variables
        package_name = None
        class_name = None
        method = None
        params = []
        param_types = []
        return_value = False

        # Parse arguments
        try:
            for i, arg in enumerate(args):
                if arg == "--package-name" and i + 1 < len(args):
                    package_name = args[i + 1]
                elif arg == "--class-name" and i + 1 < len(args):
                    class_name = args[i + 1]
                elif arg == "--method" and i + 1 < len(args):
                    method = args[i + 1]
                elif arg == "--args-int" and i + 1 < len(args):
                    param_types.append("int")
                    params.append(int(args[i + 1]))
                elif arg == "--args-string" and i + 1 < len(args):
                    param_types.append("java.lang.String")
                    params.append(str(args[i + 1]))
                elif arg == "--args-boolean" and i + 1 < len(args):
                    param_types.append("boolean")
                    params.append(args[i + 1].lower() == "true")
                elif arg == "--return-value":
                    return_value = True

            # Validate required arguments
            if not package_name or not class_name or not method:
                print("Error: --package-name, --class-name, and --method are required. Use -h or --help for usage information.")
                return

            # Call the API to invoke the method
            v = self.api.invoke_method(package_name, class_name, method, params, param_types, return_value)

            # Display the result if return_value is True
            if return_value:
                print(f'Return value: {v}')
            print(f'Invoked {package_name}.{class_name}.{method} with parameters {params} and types {param_types}')
        except Exception as e:
            print(f"Error during method invocation: {e}")


    def change_static_variable(self, args: list):
        """
            Changes a static variable of a specific Java class.

            :param args:
            :return:
        """

        help_text = """
            Usage:
            plugin hookhelper changeVar --package-name <package_name> --class-name <class_name> --variable-name <variable_name> 
                        --new-value <new_value> <--int|--string|--boolean>

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
            """

        if "-h" in args or "--help" in args:
            print(help_text)
            return

        if len(args) < 5:
            print("Error: Missing required arguments. Use -h or --help for usage information.")
            return

        package_name = None
        class_name = None
        variable_name = None
        new_value = None
        value_type = None

        # Parse arguments
        try:
            for i, arg in enumerate(args):
                if arg == "--package-name" and i + 1 < len(args):
                    package_name = args[i + 1]
                elif arg == "--class-name" and i + 1 < len(args):
                    class_name = args[i + 1]
                elif arg == "--variable-name" and i + 1 < len(args):
                    variable_name = args[i + 1]
                elif arg == "--new-value" and i + 1 < len(args):
                    new_value = args[i + 1]
                elif arg == "--int":
                    value_type = 'int'
                elif arg == "--string":
                    value_type = 'string'
                elif arg == "--boolean":
                    value_type = 'boolean'

            if not package_name or not class_name or not variable_name or not new_value or not value_type:
                print("Error: Missing required arguments. Use -h or --help for usage information.")
                return

            v = self.api.change_static_variable(package_name, class_name, variable_name, new_value, value_type)
            print(f'Static variable {variable_name} in {package_name}.{class_name} changed to {new_value} as {value_type}')
        except Exception as e:
            print(f"Error during static variable change: {e}")


    def invoke_non_static_method(self, args: list):
        """
            Invokes a specific Java class method of a non-static class and optionally returns the result.

            :param args:
            :return:
        """

        help_text = """
            Usage:
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
            """

        if "-h" in args or "--help" in args:
            print(help_text)
            return

        if len(args) < 3:
            print("Error: Missing required arguments. Use -h or --help for usage information.")
            return

        package_name = None
        class_name = None
        method = None
        params = []
        param_types = []
        return_value = False

        # Parse arguments
        try:
            for i, arg in enumerate(args):
                if arg == "--package-name" and i + 1 < len(args):
                    package_name = args[i + 1]
                elif arg == "--class-name" and i + 1 < len(args):
                    class_name = args[i + 1]
                elif arg == "--method" and i + 1 < len(args):
                    method = args[i + 1]
                elif arg == "--args-int" and i + 1 < len(args):
                    param_types.append("int")
                    params.append(int(args[i + 1]))
                elif arg == "--args-string" and i + 1 < len(args):
                    param_types.append("java.lang.String")
                    params.append(str(args[i + 1]))
                elif arg == "--args-boolean" and i + 1 < len(args):
                    param_types.append("boolean")
                    params.append(args[i + 1].lower() == "true")
                elif arg == "--return-value":
                    return_value = True

            if not package_name or not class_name or not method:
                print("Error: --package-name, --class-name, and --method are required. Use -h or --help for usage information.")
                return

            v = self.api.invoke_non_static_method(package_name, class_name, method, params, param_types, return_value)

            if return_value:
                print(f'Return value: {v}')
            print(f'Invoked {package_name}.{class_name}.{method} with parameters {params} and types {param_types}')
        except Exception as e:
            print(f"Error during method invocation: {e}")


    def parse_command_args(self, args):
        """Parse command-line arguments"""
        class_name = ""
        method_name = ""
        object_class = ""
        object_properties = []
        debug = False

        prop_pattern = re.compile(r"--object-property-(\w+)\s+(\w+)\(([\w\s]+)\)")

        for i in range(len(args)):
            arg = args[i]
            if arg == "--debug":
                debug = True
            elif arg.startswith("--class-name"):
                class_name = args[i + 1]
            elif arg.startswith("--method-name"):
                method_name = args[i + 1]
            elif arg.startswith("--object-class"):
                object_class = args[i + 1]
            elif arg.startswith("--object-property"):
                match = prop_pattern.match(" ".join(args[i:i + 2]))
                if match:
                    prop_type = match.group(1)
                    prop_name = match.group(2)
                    prop_value = match.group(3)
                    object_properties.append({
                        "type": prop_type,
                        "name": prop_name,
                        "value": prop_value
                    })

        return class_name, method_name, object_class, object_properties, debug

    def invoke_method_with_object(self, args: list):
        """Invoke the method with a flexible object instance"""

        help_text = """
            Usage:
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
            """

        if "-h" in args or "--help" in args:
            print(help_text)
            return

        try:
            class_name, method_name, object_class, object_properties, debug = self.parse_command_args(args)
            if not class_name or not method_name or not object_class:
                print("Error: Missing required arguments. Use -h or --help for usage information.")
                return

            result = self.api.invoke_method_with_object(class_name, method_name, object_class, object_properties, debug)
            print(f"Return value: {result}")
            print(f"Invoked {class_name} with method {method_name} and object {object_class}, passing properties {object_properties}")
        except Exception as e:
            print(f"Error during invocation: {e}")


    def hook_constructor(self, args: list):
        """
            Calls the RPC export method to hook the constructor

            :param args: Command-line style arguments for the constructor hook
            :return:
        """

        HELP_TEXT = """
            Usage:
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
            """
        if "-h" in args or "--help" in args:
            print(HELP_TEXT)
            return

        class_name = None
        constructor_args = []

        # Parse arguments
        for i, arg in enumerate(args):
            if arg == "--class-name" and i + 1 < len(args):
                class_name = args[i + 1]
            elif arg == "--args-int" and i + 1 < len(args):
                constructor_args.append(int(args[i + 1]))
            elif arg == "--args-string" and i + 1 < len(args):
                constructor_args.append(str(args[i + 1]))
            elif arg == "--args-boolean" and i + 1 < len(args):
                bool_value = args[i + 1].lower() in ("true", "1")
                constructor_args.append(bool_value)

        if not class_name:
            print("Error: Please provide a class name using --class-name.")
            return

        self.api.hook_constructor(class_name, constructor_args)
        print(f'Hooked constructor of class {class_name} with arguments: {constructor_args}')


namespace = 'hookhelper'
plugin = HookHelper
