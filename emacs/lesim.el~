;;; emacs syntax highlighting for lesim2
;;;
;;; version 1 by Stefano Ghirlanda
;;;
;;; this file is distributed under the same terms as lesim2
;;;
;;; this file is not complete:
;;;
;;; - comment blocks delimited by ### are not handled
;;;
;;; - anything starting with one or more uppercase characters is
;;;   highlighted as a phase line
;;;
;;; - a final underscore is highlighted in red, following the
;;;   convention that phase "help line" names end in an underscore;
;;;   this convention is not part of the lesim2 syntax and it makes no
;;;   difference whether you use it or not.

(require 'generic-x)

(define-generic-mode 'lesim2-mode
  '("#")                       ; comment character
  '(
    "behaviors"                ; keywords
    "stimulus_elements" 
    "mechanism"
    "start_v"
    "start_w"
    "alpha_v"
    "alpha_w"
    "beta"
    "behavior_cost"
    "u"
    "response_requirements"
    "bind_trials"
    "n_subjects"
    "subplottitle"
    "runlabel"
    "subject"
    "xscale"
    "xscale_match"
    "phases"
    "cumulative"
    "match"
    "filename"
    )
  '(
    ;;; title is a keyword when it is not a string:
    ("title[^']" . 'font-lock-keyword-face)
    ;;; stop:
    ("[\s-]stop:" . 'font-lock-builtin-face)
    ;;; stop:
    ("new_trial" . 'font-lock-keyword-face)
    ;;; @ commands:
    ("@\\<[a-z]*\\>[[:blank:]\n]" . 'font-lock-builtin-face)
    ;;; strings:
    ("'\\<.*?\\>'" . 'font-lock-string-face)
    ;;; LINEs
    ("\\<[A-Z]+[_A-Za-z0-9]*\\>" . 'font-lock-variable-name-face)
    ;;; various recurrent syntax fragments:
    ("_[[:blank:]\n]" 0 'font-lock-constant-face)
    ("|" . 'font-lock-constant-face)
    ("->" . 'font-lock-constant-face)
    ("-" . 'font-lock-constant-face)
    ("[^[:alpha:]][0-9]*\\.?[0-9]+" . 'font-lock-variable-name-face)
    )
  '("\\.ls2$") ; files for which to activate this mode 
  nil
  "A mode for lesim2 files" ; doc string
  )

