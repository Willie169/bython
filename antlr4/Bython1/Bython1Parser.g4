parser grammar Bython1Parser;

options {
    superClass = Bython1ParserBase;
    tokenVocab = Bython1Lexer;
}

single_input
    : NEWLINE
    | simple_stmts
    | compound_stmt NEWLINE
    ;

file_input
    : (NEWLINE | stmt)* EOF
    ;

eval_input
    : testlist NEWLINE* EOF
    ;

decorator
    : AT dotted_name (OPEN_PAREN arglist? CLOSE_PAREN)? NEWLINE
    ;

decorators
    : decorator+
    ;

decorated
    : decorators (classdef | funcdef | async_funcdef)
    ;

async_funcdef
    : ASYNC funcdef
    ;

funcdef
    : DEL name parameters (ARROW test)? OPEN_BRACE block CLOSE_BRACE SEMI_COLON
    ;

parameters
    : OPEN_PAREN typedargslist? CLOSE_PAREN
    ;

typedargslist
    : (
        tfpdef (ASSIGN test)? (COMMA tfpdef (ASSIGN test)?)* (
            COMMA (
                STAR tfpdef? (COMMA tfpdef (ASSIGN test)?)* (COMMA (POWER tfpdef COMMA?)?)?
                | POWER tfpdef COMMA?
            )?
        )?
        | STAR tfpdef? (COMMA tfpdef (ASSIGN test)?)* (COMMA (POWER tfpdef COMMA?)?)?
        | POWER tfpdef COMMA?
    )
    ;

tfpdef
    : name (COLON test)?
    ;

varargslist
    : (
        vfpdef (ASSIGN test)? (COMMA vfpdef (ASSIGN test)?)* (
            COMMA (
                STAR vfpdef? (COMMA vfpdef (ASSIGN test)?)* (COMMA (POWER vfpdef COMMA?)?)?
                | POWER vfpdef (COMMA)?
            )?
        )?
        | STAR vfpdef? (COMMA vfpdef (ASSIGN test)?)* (COMMA (POWER vfpdef COMMA?)?)?
        | POWER vfpdef COMMA?
    )
    ;

vfpdef
    : name
    ;

stmt
    : simple_stmts
    | compound_stmt
    ;

simple_stmts
    : simple_stmt (SEMI_COLON simple_stmt)* SEMI_COLON? NEWLINE
    ;

simple_stmt
    : (
        expr_stmt
        | del_stmt
        | pass_stmt
        | flow_stmt
        | import_stmt
        | global_stmt
        | nonlocal_stmt
        | assert_stmt
    )
    ;

expr_stmt
    : testlist_star_expr (
        annassign
        | augassign (yield_expr | testlist)
        | (ASSIGN (yield_expr | testlist_star_expr))*
    ) SEMI_COLON
    ;

annassign
    : COLON test (ASSIGN test)?
    ;

testlist_star_expr
    : (test | star_expr) (COMMA (test | star_expr))* COMMA?
    ;

augassign
    : (
        ADD_ASSIGN
        | SUB_ASSIGN
        | MULT_ASSIGN
        | AT_ASSIGN
        | DIV_ASSIGN
        | MOD_ASSIGN
        | AND_ASSIGN
        | OR_ASSIGN
        | XOR_ASSIGN
        | LEFT_SHIFT_ASSIGN
        | RIGHT_SHIFT_ASSIGN
        | POWER_ASSIGN
        | IDIV_ASSIGN
    )
    ;

del_stmt
    : DEF exprlist
    ;

pass_stmt
    : PASS
    ;

flow_stmt
    : break_stmt
    | continue_stmt
    | return_stmt
    | raise_stmt
    | yield_stmt
    ;

break_stmt
    : BREAK
    ;

continue_stmt
    : CONTINUE
    ;

return_stmt
    : RETURN testlist?
    ;

yield_stmt
    : yield_expr
    ;

raise_stmt
    : RAISE (test (FROM test)?)?
    ;

import_stmt
    : import_name
    | import_from
    ;

import_name
    : IMPORT dotted_as_names
    ;

import_from
    : (
        FROM ((DOT | ELLIPSIS)* dotted_name | (DOT | ELLIPSIS)+) IMPORT (
            STAR
            | OPEN_PAREN import_as_names CLOSE_PAREN
            | import_as_names
        )
    )
    ;

import_as_name
    : name (AS name)?
    ;

dotted_as_name
    : dotted_name (AS name)?
    ;

import_as_names
    : import_as_name (COMMA import_as_name)* COMMA?
    ;

dotted_as_names
    : dotted_as_name (COMMA dotted_as_name)*
    ;

dotted_name
    : name (DOT name)*
    ;

global_stmt
    : GLOBAL name (COMMA name)*
    ;

nonlocal_stmt
    : NONLOCAL name (COMMA name)*
    ;

assert_stmt
    : ASSERT test (COMMA test)?
    ;

compound_stmt
    : if_stmt
    | while_stmt
    | for_stmt
    | try_stmt
    | with_stmt
    | funcdef
    | classdef
    | decorated
    | async_stmt
    | match_stmt
    ;

async_stmt
    : ASYNC (funcdef | with_stmt | for_stmt)
    ;

if_stmt
    : IF test OPEN_BRACE block CLOSE_BRACE (ELIF test OPEN_BRACE block CLOSE_BRACE)* (ELSE OPEN_BRACE block CLOSE_BRACE)?
    ;

while_stmt
    : WHILE test OPEN_BRACE block CLOSE_BRACE (ELSE OPEN_BRACE block CLOSE_BRACE)?
    ;

for_stmt
    : FOR exprlist IN testlist OPEN_BRACE block CLOSE_BRACE (ELSE OPEN_BRACE block CLOSE_BRACE)?
    ;

try_stmt
    : (
        TRY OPEN_BRACE block CLOSE_BRACE (
            (except_clause OPEN_BRACE block CLOSE_BRACE)+ (ELSE OPEN_BRACE block CLOSE_BRACE)? (FINALLY OPEN_BRACE block CLOSE_BRACE)?
            | FINALLY OPEN_BRACE block CLOSE_BRACE
        )
    )
    ;

with_stmt
    : WITH with_item (COMMA with_item)* OPEN_BRACE block CLOSE_BRACE
    ;

with_item
    : test (AS expr)?
    ;

except_clause
    : EXCEPT (test (AS name)?)?
    ;

block
    : simple_stmts
    | NEWLINE stmt+
    ;

match_stmt
    : MATCH subject_expr OPEN_BRACE case_block+ CLOSE_BRACE
    ;

subject_expr
    : star_named_expression COMMA star_named_expressions?
    | test
    ;

star_named_expressions
    : COMMA star_named_expression+ COMMA?
    ;

star_named_expression
    : STAR expr
    | test
    ;

case_block
    : CASE patterns guard? OPEN_BRACE block CLOSE_BRACE
    ;

guard
    : IF test
    ;

patterns
    : open_sequence_pattern
    | pattern
    ;

pattern
    : as_pattern
    | or_pattern
    ;

as_pattern
    : or_pattern AS pattern_capture_target
    ;

or_pattern
    : closed_pattern (OR_OP closed_pattern)*
    ;

closed_pattern
    : literal_pattern
    | capture_pattern
    | wildcard_pattern
    | value_pattern
    | group_pattern
    | sequence_pattern
    | mapping_pattern
    | class_pattern
    ;

literal_pattern
    : signed_number { this.CannotBePlusMinus() }?
    | complex_number
    | strings
    | NONE
    | TRUE
    | FALSE
    ;

literal_expr
    : signed_number { this.CannotBePlusMinus() }?
    | complex_number
    | strings
    | NONE
    | TRUE
    | FALSE
    ;

complex_number
    : signed_real_number ADD imaginary_number
    | signed_real_number MINUS imaginary_number
    ;

signed_number
    : NUMBER
    | MINUS NUMBER
    ;

signed_real_number
    : real_number
    | MINUS real_number
    ;

real_number
    : NUMBER
    ;

imaginary_number
    : NUMBER
    ;

capture_pattern
    : pattern_capture_target
    ;

pattern_capture_target
    :  name { this.CannotBeDotLpEq() }?
    ;

wildcard_pattern
    : UNDERSCORE
    ;

value_pattern
    : attr { this.CannotBeDotLpEq() }?
    ;

attr
    : name (DOT name)+
    ;

name_or_attr
    : attr
    | name
    ;

group_pattern
    : OPEN_PAREN pattern CLOSE_PAREN
    ;

sequence_pattern
    : OPEN_BRACK maybe_sequence_pattern? CLOSE_BRACK
    | OPEN_PAREN open_sequence_pattern? CLOSE_PAREN
    ;

open_sequence_pattern
    : maybe_star_pattern COMMA maybe_sequence_pattern?
    ;

maybe_sequence_pattern
    : maybe_star_pattern (COMMA maybe_star_pattern)* COMMA?
    ;

maybe_star_pattern
    : star_pattern
    | pattern
    ;

star_pattern
    : STAR pattern_capture_target
    | STAR wildcard_pattern
    ;

mapping_pattern
    : OPEN_BRACE CLOSE_BRACE
    | OPEN_BRACE double_star_pattern COMMA? CLOSE_BRACE
    | OPEN_BRACE items_pattern COMMA double_star_pattern COMMA? CLOSE_BRACE
    | OPEN_BRACE items_pattern COMMA? CLOSE_BRACE
    ;

items_pattern
    : key_value_pattern (COMMA key_value_pattern)*
    ;

key_value_pattern
    : (literal_expr | attr) COLON pattern
    ;

double_star_pattern
    : POWER pattern_capture_target
    ;

class_pattern
    : name_or_attr OPEN_PAREN CLOSE_PAREN
    | name_or_attr OPEN_PAREN positional_patterns COMMA? CLOSE_PAREN
    | name_or_attr OPEN_PAREN keyword_patterns COMMA? CLOSE_PAREN
    | name_or_attr OPEN_PAREN positional_patterns COMMA keyword_patterns COMMA? CLOSE_PAREN
    ;

positional_patterns
    : pattern (COMMA pattern)*
    ;

keyword_patterns
    : keyword_pattern (COMMA keyword_pattern)*
    ;

keyword_pattern
    : name ASSIGN pattern
    ;

test
    : or_test (IF or_test ELSE test)?
    | lambdef
    ;

test_nocond
    : or_test
    | lambdef_nocond
    ;

lambdef
    : LAMBDA varargslist? OPEN_BRACE test CLOSE_BRACE
    ;

lambdef_nocond
    : LAMBDA varargslist? OPEN_BRACE test_nocond CLOSE_BRACE
    ;

or_test
    : and_test ((OR) and_test)*
    ;

and_test
    : not_test ((AND) not_test)*
    ;

not_test
    : NOT not_test
    | comparison
    ;

comparison
    : expr (comp_op expr)*
    ;

comp_op
    : LESS_THAN
    | GREATER_THAN
    | EQUALS
    | GT_EQ
    | LT_EQ
    | NOT_EQ_1
    | NOT_EQ_2
    | IN
    | NOT IN
    | IS
    | IS NOT
    ;

star_expr
    : STAR expr
    ;

expr
    : atom_expr
    | expr POWER expr
    | (ADD | MINUS | NOT_OP)+ expr
    | expr (STAR | AT | DIV | MOD | IDIV) expr
    | expr (ADD | MINUS) expr
    | expr (LEFT_SHIFT | RIGHT_SHIFT) expr
    | expr AND_OP expr
    | expr XOR expr
    | expr OR_OP expr
    ;

atom_expr
    : AWAIT? atom trailer*
    ;

atom
    : OPEN_PAREN (yield_expr | testlist_comp)? CLOSE_PAREN
    | OPEN_BRACK testlist_comp? CLOSE_BRACK
    | OPEN_BRACE dictorsetmaker? CLOSE_BRACE
    | name
    | NUMBER
    | STRING+
    | ELLIPSIS
    | NONE
    | TRUE
    | FALSE
    ;

name
    : NAME
    | UNDERSCORE
    | MATCH
    ;

testlist_comp
    : (test | star_expr) (comp_for | (COMMA (test | star_expr))* COMMA?)
    ;

trailer
    : OPEN_PAREN arglist? CLOSE_PAREN
    | OPEN_BRACK subscriptlist CLOSE_BRACK
    | DOT name
    ;

subscriptlist
    : subscript_ (COMMA subscript_)* COMMA?
    ;

subscript_
    : test
    | test? COLON test? sliceop?
    ;

sliceop
    : COLON test?
    ;

exprlist
    : (expr | star_expr) (COMMA (expr | star_expr))* COMMA?
    ;

testlist
    : test (COMMA test)* COMMA?
    ;

dictorsetmaker
    : (
        ((test COLON test | POWER expr) (comp_for | (COMMA (test COLON test | POWER expr))* COMMA?))
        | ((test | star_expr) (comp_for | (COMMA (test | star_expr))* COMMA?))
    )
    ;

classdef
    : CLASS name (OPEN_PAREN arglist? CLOSE_PAREN)? OPEN_BRACE block CLOSE_BRACE
    ;

arglist
    : argument (COMMA argument)* COMMA?
    ;

argument
    : (test comp_for? | test ASSIGN test | POWER test | STAR test)
    ;

comp_iter
    : comp_for
    | comp_if
    ;

comp_for
    : ASYNC? FOR exprlist IN or_test comp_iter?
    ;

comp_if
    : IF test_nocond comp_iter?
    ;

encoding_decl
    : name
    ;

yield_expr
    : YIELD yield_arg?
    ;

yield_arg
    : FROM test
    | testlist
    ;

strings
    : STRING+
    ;