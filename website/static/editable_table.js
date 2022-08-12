$(document).ready(function() {
    const $tableID = $('#table');
    const newTr = `
    <tr class="hide">
        <td class="pt-3-half" contenteditable="false">
            <input type="text" name="time_value" value=" " style="display:table-cell; width:100%">
        </td>
        <td class="pt-3-half" contenteditable="false">
            <input type="text" name="data_value" value=" " style="display:table-cell; width:100%">
        </td>
        <td class="pt-3-half" contenteditable="false">
            <input type="text" name="data_annotation" value=" " style="display:table-cell; width:100%">
        </td>
        <td class="pt-3-half">
            <span class="table-up">
                <a href="#!" class="indigo-text">
                    <i class="fas fa-long-arrow-alt-up" aria-hidden="true"></i>
                </a>
            </span>
            <span class="table-down">
                <a href="#!" class="indigo-text">
                    <i class="fas fa-long-arrow-alt-down" aria-hidden="true"></i>
                </a>
            </span>
        </td>
        <td>
            <span class="table-remove">
                <button
                    type="button"
                    class="btn btn-danger btn-rounded btn-sm my-0 waves-effect waves-light">
                    Remove
                </button>
            </span>
        </td>
    </tr>
    `;

    $('.table-add').on('click', 'i', () => {
        $n_rows = $tableID.find('tbody tr').length
        const $clone = $tableID.find('tbody tr').last().clone(true).removeClass('hide table-line');
        if ($tableID.find('tbody tr').length === 0) {
            $('tbody').append(newTr);
        }
        
        // Set new names of the input fields in the cloned tr
        // const $inputs = $clone.find('input');
        // for (let i = 0; i < $inputs.length; i++) {
        //     $old_name = $inputs.get(i).name;
        //     if ($old_name.startsWith('time_value')) {
        //         $new_name = 'time_value' + $n_rows.toString();
        //     }
        //     else if ($old_name.startsWith('data_value')) {
        //         $new_name = 'data_value' + $n_rows.toString();
        //     }
        //     $inputs.get(i).setAttribute('name', $new_name);
        // }
        
        $tableID.find('table').append($clone);
    });
    
    $tableID.on('click', '.table-remove', function () {
        $(this).parents('tr').detach();
    });

    $tableID.on('click', '.table-up', function () {
        const $row = $(this).parents('tr');
        if ($row.index() === 0) { return; }
        $row.prev().before($row.get(0));
    });
    
    $tableID.on('click', '.table-down', function () {
        const $row = $(this).parents('tr');
        $row.next().after($row.get(0));
    });
    
    
});
